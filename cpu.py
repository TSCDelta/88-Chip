import pytest


class Chip8CPU:
    def __init__(self):
        self.memory = [0] * 4096
        self.V = [0] * 16
        self.I = 0
        self.pc = 0x200
        self.stack = []
        self.delay_timer = 0
        self.sound_timer = 0
        self.display = [[0] * 64 for _ in range(32)]
        self.keypad = [0] * 16
        
        # Load minimal font set
        fonts = [0xF0,0x90,0x90,0x90,0xF0, 0x20,0x60,0x20,0x20,0x70]  # 0,1 only
        for i, b in enumerate(fonts):
            self.memory[0x50 + i] = b

    def execute(self, inst):
        op = (inst & 0xF000) >> 12
        x = (inst & 0x0F00) >> 8
        y = (inst & 0x00F0) >> 4
        n = inst & 0x000F
        nn = inst & 0x00FF
        nnn = inst & 0x0FFF
        
        if inst == 0x00E0:  # CLS
            for row in range(32):
                for col in range(64):
                    self.display[row][col] = 0
        elif inst == 0x00EE:  # RET
            self.pc = self.stack.pop()
        elif op == 0x1:  # JP
            self.pc = nnn
        elif op == 0x2:  # CALL
            self.stack.append(self.pc)
            self.pc = nnn
        elif op == 0x3:  # SE Vx, byte
            if self.V[x] == nn:
                self.pc += 2
        elif op == 0x4:  # SNE Vx, byte
            if self.V[x] != nn:
                self.pc += 2
        elif op == 0x5:  # SE Vx, Vy
            if self.V[x] == self.V[y]:
                self.pc += 2
        elif op == 0x6:  # LD Vx, byte
            self.V[x] = nn
        elif op == 0x7:  # ADD Vx, byte
            self.V[x] = (self.V[x] + nn) & 0xFF
        elif op == 0x8:
            if n == 0x0:  # LD Vx, Vy
                self.V[x] = self.V[y]
            elif n == 0x1:  # OR
                self.V[x] |= self.V[y]
            elif n == 0x2:  # AND
                self.V[x] &= self.V[y]
            elif n == 0x3:  # XOR
                self.V[x] ^= self.V[y]
            elif n == 0x4:  # ADD Vx, Vy
                result = self.V[x] + self.V[y]
                self.V[0xF] = 1 if result > 255 else 0
                self.V[x] = result & 0xFF
            elif n == 0x5:  # SUB
                self.V[0xF] = 1 if self.V[x] >= self.V[y] else 0
                self.V[x] = (self.V[x] - self.V[y]) & 0xFF
            elif n == 0x6:  # SHR
                self.V[0xF] = self.V[x] & 0x1
                self.V[x] >>= 1
            elif n == 0x7:  # SUBN
                self.V[0xF] = 1 if self.V[y] >= self.V[x] else 0
                self.V[x] = (self.V[y] - self.V[x]) & 0xFF
            elif n == 0xE:  # SHL
                self.V[0xF] = (self.V[x] & 0x80) >> 7
                self.V[x] = (self.V[x] << 1) & 0xFF
        elif op == 0x9:  # SNE Vx, Vy
            if self.V[x] != self.V[y]:
                self.pc += 2
        elif op == 0xA:  # LD I, addr
            self.I = nnn
        elif op == 0xB:  # JP V0, addr
            self.pc = nnn + self.V[0]
        elif op == 0xC:  # RND (simplified - returns 0x42)
            self.V[x] = 0x42 & nn
        elif op == 0xD:  # DRW
            x_pos = self.V[x] % 64
            y_pos = self.V[y] % 32
            self.V[0xF] = 0
            for row in range(n):
                if y_pos + row >= 32:
                    break
                sprite_byte = self.memory[self.I + row]
                for col in range(8):
                    if x_pos + col >= 64:
                        break
                    if (sprite_byte & (0x80 >> col)) != 0:
                        if self.display[y_pos + row][x_pos + col] == 1:
                            self.V[0xF] = 1
                        self.display[y_pos + row][x_pos + col] ^= 1
        elif op == 0xE:
            if nn == 0x9E:  # SKP
                if self.keypad[self.V[x]] == 1:
                    self.pc += 2
            elif nn == 0xA1:  # SKNP
                if self.keypad[self.V[x]] == 0:
                    self.pc += 2
        elif op == 0xF:
            if nn == 0x07:  # LD Vx, DT
                self.V[x] = self.delay_timer
            elif nn == 0x0A:  # LD Vx, K
                for i, key in enumerate(self.keypad):
                    if key == 1:
                        self.V[x] = i
                        return
                self.pc -= 2
            elif nn == 0x15:  # LD DT, Vx
                self.delay_timer = self.V[x]
            elif nn == 0x18:  # LD ST, Vx
                self.sound_timer = self.V[x]
            elif nn == 0x1E:  # ADD I, Vx
                self.I += self.V[x]
            elif nn == 0x29:  # LD F, Vx
                self.I = 0x50 + (self.V[x] * 5)
            elif nn == 0x33:  # LD B, Vx
                self.memory[self.I] = self.V[x] // 100
                self.memory[self.I + 1] = (self.V[x] // 10) % 10
                self.memory[self.I + 2] = self.V[x] % 10
            elif nn == 0x55:  # LD [I], Vx
                for i in range(x + 1):
                    self.memory[self.I + i] = self.V[i]
            elif nn == 0x65:  # LD Vx, [I]
                for i in range(x + 1):
                    self.V[i] = self.memory[self.I + i]

    def cycle(self):
        inst = (self.memory[self.pc] << 8) | self.memory[self.pc + 1]
        self.pc += 2
        self.execute(inst)
        if self.delay_timer > 0:
            self.delay_timer -= 1
        if self.sound_timer > 0:
            self.sound_timer -= 1


# Minimal tests
def test_cls():
    cpu = Chip8CPU()
    cpu.display[0][0] = 1
    cpu.execute(0x00E0)
    assert cpu.display[0][0] == 0

def test_ret():
    cpu = Chip8CPU()
    cpu.stack.append(0x300)
    cpu.execute(0x00EE)
    assert cpu.pc == 0x300

def test_jp():
    cpu = Chip8CPU()
    cpu.execute(0x1ABC)
    assert cpu.pc == 0xABC

def test_call():
    cpu = Chip8CPU()
    cpu.pc = 0x250
    cpu.execute(0x2ABC)
    assert cpu.pc == 0xABC and cpu.stack[-1] == 0x250

def test_se_byte():
    cpu = Chip8CPU()
    cpu.V[1] = 0x55
    cpu.pc = 0x200
    cpu.execute(0x3155)
    assert cpu.pc == 0x202

def test_sne_byte():
    cpu = Chip8CPU()
    cpu.V[1] = 0x55
    cpu.pc = 0x200
    cpu.execute(0x4144)
    assert cpu.pc == 0x202

def test_se_reg():
    cpu = Chip8CPU()
    cpu.V[1] = cpu.V[2] = 0x55
    cpu.pc = 0x200
    cpu.execute(0x5120)
    assert cpu.pc == 0x202

def test_ld_byte():
    cpu = Chip8CPU()
    cpu.execute(0x6155)
    assert cpu.V[1] == 0x55

def test_add_byte():
    cpu = Chip8CPU()
    cpu.V[1] = 0x10
    cpu.execute(0x7120)
    assert cpu.V[1] == 0x30

def test_ld_reg():
    cpu = Chip8CPU()
    cpu.V[2] = 0x55
    cpu.execute(0x8120)
    assert cpu.V[1] == 0x55

def test_or():
    cpu = Chip8CPU()
    cpu.V[1] = 0xF0
    cpu.V[2] = 0x0F
    cpu.execute(0x8121)
    assert cpu.V[1] == 0xFF

def test_and():
    cpu = Chip8CPU()
    cpu.V[1] = 0xF0
    cpu.V[2] = 0x0F
    cpu.execute(0x8122)
    assert cpu.V[1] == 0x00

def test_xor():
    cpu = Chip8CPU()
    cpu.V[1] = 0xF0
    cpu.V[2] = 0x0F
    cpu.execute(0x8123)
    assert cpu.V[1] == 0xFF

def test_add_carry():
    cpu = Chip8CPU()
    cpu.V[1] = 0xFF
    cpu.V[2] = 0x01
    cpu.execute(0x8124)
    assert cpu.V[1] == 0x00 and cpu.V[0xF] == 1

def test_sub():
    cpu = Chip8CPU()
    cpu.V[1] = 0x30
    cpu.V[2] = 0x20
    cpu.execute(0x8125)
    assert cpu.V[1] == 0x10 and cpu.V[0xF] == 1

def test_shr():
    cpu = Chip8CPU()
    cpu.V[1] = 0x05
    cpu.execute(0x8126)
    assert cpu.V[1] == 0x02 and cpu.V[0xF] == 1

def test_subn():
    cpu = Chip8CPU()
    cpu.V[1] = 0x20
    cpu.V[2] = 0x30
    cpu.execute(0x8127)
    assert cpu.V[1] == 0x10 and cpu.V[0xF] == 1

def test_shl():
    cpu = Chip8CPU()
    cpu.V[1] = 0x82
    cpu.execute(0x812E)
    assert cpu.V[1] == 0x04 and cpu.V[0xF] == 1

def test_sne_reg():
    cpu = Chip8CPU()
    cpu.V[1] = 0x55
    cpu.V[2] = 0x44
    cpu.pc = 0x200
    cpu.execute(0x9120)
    assert cpu.pc == 0x202

def test_ld_i():
    cpu = Chip8CPU()
    cpu.execute(0xAABC)
    assert cpu.I == 0xABC

def test_jp_v0():
    cpu = Chip8CPU()
    cpu.V[0] = 0x10
    cpu.execute(0xB200)
    assert cpu.pc == 0x210

def test_rnd():
    cpu = Chip8CPU()
    cpu.execute(0xC1FF)
    assert cpu.V[1] == 0x42

def test_draw():
    cpu = Chip8CPU()
    cpu.V[1] = cpu.V[2] = 10
    cpu.I = 0x300
    cpu.memory[0x300] = 0xF0
    cpu.execute(0xD121)
    assert cpu.display[10][10] == 1

def test_skp():
    cpu = Chip8CPU()
    cpu.V[1] = 0x5
    cpu.keypad[0x5] = 1
    cpu.pc = 0x200
    cpu.execute(0xE19E)
    assert cpu.pc == 0x202

def test_sknp():
    cpu = Chip8CPU()
    cpu.V[1] = 0x5
    cpu.pc = 0x200
    cpu.execute(0xE1A1)
    assert cpu.pc == 0x202

def test_ld_dt():
    cpu = Chip8CPU()
    cpu.delay_timer = 0x30
    cpu.execute(0xF107)
    assert cpu.V[1] == 0x30

def test_wait_key():
    cpu = Chip8CPU()
    cpu.pc = 0x200
    cpu.keypad[0x5] = 1
    cpu.execute(0xF10A)
    assert cpu.V[1] == 0x5

def test_set_dt():
    cpu = Chip8CPU()
    cpu.V[1] = 0x30
    cpu.execute(0xF115)
    assert cpu.delay_timer == 0x30

def test_set_st():
    cpu = Chip8CPU()
    cpu.V[1] = 0x30
    cpu.execute(0xF118)
    assert cpu.sound_timer == 0x30

def test_add_i():
    cpu = Chip8CPU()
    cpu.I = 0x200
    cpu.V[1] = 0x50
    cpu.execute(0xF11E)
    assert cpu.I == 0x250

def test_font():
    cpu = Chip8CPU()
    cpu.V[1] = 0xA
    cpu.execute(0xF129)
    assert cpu.I == 0x50 + (0xA * 5)

def test_bcd():
    cpu = Chip8CPU()
    cpu.V[1] = 123
    cpu.I = 0x300
    cpu.execute(0xF133)
    assert cpu.memory[0x300:0x303] == [1, 2, 3]

def test_store():
    cpu = Chip8CPU()
    cpu.V[0] = 0x10
    cpu.V[1] = 0x20
    cpu.I = 0x300
    cpu.execute(0xF155)
    assert cpu.memory[0x300:0x302] == [0x10, 0x20]

def test_load():
    cpu = Chip8CPU()
    cpu.memory[0x300:0x302] = [0x10, 0x20]
    cpu.I = 0x300
    cpu.execute(0xF165)
    assert cpu.V[0] == 0x10 and cpu.V[1] == 0x20

def test_cycle():
    cpu = Chip8CPU()
    cpu.memory[0x200:0x202] = [0x61, 0x55]
    cpu.cycle()
    assert cpu.V[1] == 0x55 and cpu.pc == 0x202

def test_timers():
    cpu = Chip8CPU()
    cpu.delay_timer = cpu.sound_timer = 5
    cpu.memory[0x200:0x202] = [0x00, 0xE0]
    cpu.cycle()
    assert cpu.delay_timer == 4 and cpu.sound_timer == 4


if __name__ == "__main__":
    pytest.main([__file__])