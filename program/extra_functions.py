import time
import sys


class ExtraFunctions:




    def create_colored_string(self, text, text_color, background_color):
        color_code = f"\033[1;{text_color};{background_color}m"
        colored_string = f"{color_code}{text}\033[m"
        return colored_string
        # colored_string = create_colored_string("Hello, World!", "31", "47")
        # print(colored_string)


    def loading_animation(self):
        animation = "|/-\\"
        for i in range(100):
            time.sleep(0.1)
            sys.stdout.write("\r" + animation[i % len(animation)])
            sys.stdout.flush()
        print("\nLoading complete!")