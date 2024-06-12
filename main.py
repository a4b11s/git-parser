import merge_and_clean
import parse_urls
import parse_repos
import sys

def main(mode):
    if mode == 'help':
        print('Available modes: merge, urls, repos, all')
    elif mode =='merge':
        merge_and_clean.start()
    elif mode == 'urls':
        parse_urls.start()
    elif mode == 'repos':
        parse_repos.start()
    elif mode == 'all':
        parse_urls.start()
        parse_repos.start()
        merge_and_clean.start()
    else:
        print(f'Wrong mode: {mode}, use "help" to see available modes')
        
    

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'help'
    main(mode)