import random
import pygame
from game.text_box import TextBox
 
class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.words = ["PYTHON", "PYGAME", "PLANET", "ROCKET", "GALAXY", "STREAM", "PUZZLE", "ALGORITHM"]
        self.secret_word = ""
        self.scrambled_word = ""

        self.score = 0
        self.feedback_msg = "Unscramble the letters above!"
        self.feedback_color = (210, 215, 225)

        self.input_box = TextBox(width // 2 - 130, 210, 160, 46)
        self.submit_btn = pygame.Rect(width // 2 + 45, 210, 95, 46)
        self.hint_btn = pygame.Rect(width // 2 + 150, 210, 95, 46)
        self.font_hint = pygame.font.SysFont(None, 32)

        self.font_title = pygame.font.SysFont(None, 40)
        self.font_word = pygame.font.SysFont(None, 52)
        self.font_msg = pygame.font.SysFont(None, 26)
        self.font_btn = pygame.font.SysFont(None, 24)
        self.round_duration = 30000  # ms
        self.font_tile = pygame.font.SysFont(None, 40)
        self.tile_w, self.tile_h, self.tile_gap, self.tile_y = 42, 52, 8, 108
        self.next_round()

    def scramble_string(self, word):
        letters = list(word)
        while True:
            random.shuffle(letters)
            shuffled = "".join(letters)
            if shuffled != word or len(word) <= 1:
                return shuffled

    def next_round(self):
        self.secret_word = random.choice(self.words)
        self.scrambled_word = self.scramble_string(self.secret_word)
        self.tiles = list(self.scrambled_word)   
        self.selected_tile = None  
        self.revealed = set()
        self.round_start = pygame.time.get_ticks()
        self.input_box.clear()

    def use_hint(self):
        hidden = [i for i in range(len(self.secret_word)) if i not in self.revealed]
        if len(hidden) <= 1:
            self.feedback_msg = "No more hints available!"
            self.feedback_color = (240, 170, 50)
            return
        self.revealed.add(random.choice(hidden))
        self.feedback_msg = "Hint used: -0.25 points this round."
        self.feedback_color = (240, 170, 50)

    def tile_rects(self):
        n = len(self.tiles)
        total = n * self.tile_w + (n - 1) * self.tile_gap
        x0 = self.width // 2 - total // 2
        return [
            pygame.Rect(x0 + i * (self.tile_w + self.tile_gap), self.tile_y, self.tile_w, self.tile_h)
            for i in range(n)
        ]

    def handle_tile_click(self, pos):
        for i, rect in enumerate(self.tile_rects()):
            if rect.collidepoint(pos):
                if self.selected_tile is None:
                    self.selected_tile = i
                elif self.selected_tile == i:
                    self.selected_tile = None
                else:
                    j = self.selected_tile
                    self.tiles[i], self.tiles[j] = self.tiles[j], self.tiles[i]
                    self.selected_tile = None
                return True
        return False

    def time_left_ms(self):
        elapsed = pygame.time.get_ticks() - self.round_start
        return max(0, self.round_duration - elapsed)

    def submit_guess(self):
        guess = self.input_box.text.strip().upper()
        if not guess:
            self.feedback_msg = "Type a word before submitting!"
            self.feedback_color = (240, 170, 50)
            return

        is_correct = (guess == self.secret_word)

        if is_correct:
            self.score += max(0, 1 - 0.25 * len(self.revealed))
            self.feedback_msg = f"CORRECT! '{self.secret_word}' is right."
            self.feedback_color = (80, 230, 110)
            self.next_round()
        else:
            self.feedback_msg = "WRONG GUESS! Try again."
            self.feedback_color = (240, 80, 80)
            self.input_box.clear()

    def handle_event(self, event):
        self.input_box.handle_event(event)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self.submit_guess()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.submit_btn.collidepoint(event.pos):
                self.submit_guess()
            elif self.hint_btn.collidepoint(event.pos):
                self.use_hint()
                self.input_box.active = True
            elif self.handle_tile_click(event.pos):
                self.input_box.active = True

    def update(self):
        if self.time_left_ms() <= 0:
            self.feedback_msg = f"TIME'S UP! The word was '{self.secret_word}'"
            self.feedback_color = (240, 80, 80)
            self.next_round()

    def render(self, screen):
        screen.fill((26, 30, 38))

        title_surf = self.font_title.render("Word Scramble Arena", True, (245, 245, 245))
        screen.blit(title_surf, (self.width // 2 - title_surf.get_width() // 2, 25))

        score_surf = self.font_msg.render(f"Score: {self.score:g}", True, (255, 220, 80))
        screen.blit(score_surf, (self.width // 2 - score_surf.get_width() // 2, 70))
        for i, (rect, ch) in enumerate(zip(self.tile_rects(), self.tiles)):
            selected = (i == self.selected_tile)
            fill = (100, 200, 255) if selected else (45, 52, 66)
            border = (255, 220, 80) if selected else (100, 200, 255)
            text_color = (26, 30, 38) if selected else (100, 200, 255)
            pygame.draw.rect(screen, fill, rect, border_radius=8)
            pygame.draw.rect(screen, border, rect, width=3, border_radius=8)
            letter = self.font_tile.render(ch, True, text_color)
            screen.blit(letter, (rect.centerx - letter.get_width() // 2, rect.centery - letter.get_height() // 2))
        hint_line = " ".join(
            ch if i in self.revealed else "_" for i, ch in enumerate(self.secret_word)
        )
        hint_surf = self.font_hint.render(hint_line, True, (255, 220, 80))
        screen.blit(hint_surf, (self.width // 2 - hint_surf.get_width() // 2, 178))

        self.input_box.render(screen)

        pygame.draw.rect(screen, (50, 150, 85), self.submit_btn, border_radius=6)
        pygame.draw.rect(screen, (220, 220, 220), self.submit_btn, width=2, border_radius=6)
        btn_text = self.font_btn.render("SUBMIT", True, (255, 255, 255))
        screen.blit(btn_text, (self.submit_btn.centerx - btn_text.get_width() // 2, self.submit_btn.centery - btn_text.get_height() // 2))
        pygame.draw.rect(screen, (50, 150, 85), self.hint_btn, border_radius=6)
        pygame.draw.rect(screen, (220, 220, 220), self.hint_btn, width=2, border_radius=6)
        hint_text = self.font_btn.render("HINT", True, (255, 255, 255))
        screen.blit(hint_text, (self.hint_btn.centerx - hint_text.get_width() // 2, self.hint_btn.centery - hint_text.get_height() // 2))
        feedback_surf = self.font_msg.render(self.feedback_msg, True, self.feedback_color)
        screen.blit(feedback_surf, (self.width // 2 - feedback_surf.get_width() // 2, 285))
        bar_w, bar_h = 300, 14
        bar_x = self.width // 2 - bar_w // 2
        bar_y = 320
        frac = self.time_left_ms() / self.round_duration

        if frac > 0.5:
            bar_color = (80, 230, 110)    # green
        elif frac > 0.25:
            bar_color = (240, 170, 50)    # orange
        else:
            bar_color = (240, 80, 80)     # red

        pygame.draw.rect(screen, (50, 55, 65), (bar_x, bar_y, bar_w, bar_h), border_radius=6)
        pygame.draw.rect(screen, bar_color, (bar_x, bar_y, int(bar_w * frac), bar_h), border_radius=6)
