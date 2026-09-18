import requests
import time
import sys

# Force the command terminal console to output clean unicode text strings safely
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

class RateLimiter:
    def __init__(self, max_requests_per_second=1.5):
        self.delay = 1.0 / max_requests_per_second
        self.last_request_time = 0.0

    def wait(self):
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
        self.last_request_time = time.time()

def get_opponents_from_chess_com(username, user_agent, limiter):
    headers = {'User-Agent': user_agent}
    opponents = set()
    username_clean = username.lower().strip()
    
    # Step 1: Check live endpoint first
    live_games_url = f"https://api.chess.com/pub/player/{username_clean}/games"
    try:
        limiter.wait()
        live_res = requests.get(live_games_url, headers=headers)
        if live_res.status_code == 200:
            live_games = live_res.json().get('games', [])
            for game in live_games:
                white = game.get('white', {}).get('username', '').lower()
                black = game.get('black', {}).get('username', '').lower()
                if white == username_clean and black: opponents.add(black)
                elif black == username_clean and white: opponents.add(white)
    except Exception as e:
        print(f"   ⚠️ Live games check skipped for {username_clean} ({e})")

    # Step 2: Grab long-term history archives
    archive_list_url = f"https://api.chess.com/pub/player/{username_clean}/games/archives"
    try:
        limiter.wait()
        response = requests.get(archive_list_url, headers=headers)
        
        if response.status_code != 200:
            print(f"   ❌ API Request failed for {username_clean}. Status code: {response.status_code}")
            if response.status_code == 429:
                print("   🛑 Chess.com is rate limiting us! Slowing down down the script...")
                time.sleep(3) # Heavy safety cooldown block
            return sorted(list(opponents))
        
        archives = response.json().get('archives', [])
        if not archives:
            print(f"   ❓ No archives found in database for user: {username_clean}")
            return sorted(list(opponents))
        
        # Step backwards through history files until a month yields historical matches
        for latest_archive_url in reversed(archives):
            print(f"   📂 Checking history segment: {latest_archive_url.split('/')[-2]}-{latest_archive_url.split('/')[-1]}")
            limiter.wait()
            games_response = requests.get(latest_archive_url, headers=headers)
            
            if games_response.status_code != 200:
                continue
            
            games = games_response.json().get('games', [])
            if not games:
                print("      Empty month record, stepping back another month...")
                continue
                
            for game in games:
                white = game.get('white', {}).get('username', '').lower()
                black = game.get('black', {}).get('username', '').lower()
                if white == username_clean and black: opponents.add(black)
                elif black == username_clean and white: opponents.add(white)
            
            # If we found matches in this month block, break out safely!
            if len(opponents) > 0:
                print(f"      Success! Gathered {len(opponents)} active opponents from this archive block.")
                break
                
    except Exception as e:
        print(f"   ⚠️ Connection Error for {username_clean}: {e}")
        
    return sorted(list(opponents))

def build_tree_string(username, current_depth, max_depth, user_agent, limiter, global_visited, prefix=""):
    if current_depth > max_depth:
        return ""

    username_clean = username.lower().strip()
    print(f"\n🌲 [Level {current_depth}] Mapping connections for: {username_clean}")
    
    opponents = get_opponents_from_chess_com(username_clean, user_agent, limiter)
    
    # Level 1 retrieves all matching nodes. Levels 2 and 3 cap at the first 5 entries
    if current_depth == 1:
        display_opponents = [o for o in opponents if o != username_clean]
    else:
        filtered = [o for o in opponents if o != username_clean and o not in global_visited]
        display_opponents = filtered[:5]
    
    tree_output = ""
    for i, opp in enumerate(display_opponents):
        is_last = (i == len(display_opponents) - 1)
        pointer = "└── " if is_last else "├── "
        
        # Build layout output line item
        tree_output += f"{prefix}{pointer}{opp}\n"
        
        if current_depth < max_depth:
            global_visited.add(opp)
            new_prefix = prefix + ("    " if is_last else "│   ")
            tree_output += build_tree_string(opp, current_depth + 1, max_depth, user_agent, limiter, global_visited, new_prefix)
            
    return tree_output

def generate_chess_tree_file(start_user, max_depth=3):
    # 📌 IMPORTANT: Put your email here to establish clear API logging identity
    user_agent = "ChessTreeSpider/1.5 (contact: real_user@example.com)"
    limiter = RateLimiter(max_requests_per_second=1.5)
    
    global_visited = set([start_user.lower().strip()])
    
    print(f"⚙️ Building Windows 'tree /f' structural map for: {start_user}...")
    
    file_content = f"{start_user.lower().strip()}\n"
    file_content += build_tree_string(
        username=start_user, 
        current_depth=1, 
        max_depth=max_depth, 
        user_agent=user_agent, 
        limiter=limiter, 
        global_visited=global_visited
    )
    
    filename = "chess_tree.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(file_content)
        
    print(f"\n✅ Execution Finished! Check layout inside file: {filename}")

if __name__ == "__main__":
    generate_chess_tree_file(start_user="magnuscarlsen", max_depth=3)
