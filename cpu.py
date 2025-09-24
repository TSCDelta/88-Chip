import pytest
import random


class Chip8CPU:
    def __init__(self):
        # Memory (4KB)
        self.memory = [0] * 4096
        
        # Registers
        self.V = [0] * 16  # V0-VF registers
        self.I = 0         # Index register
        self.pc = 0x200    # Program counter (starts at 0x200)
        
        # Stack
        self.stack = []
        
        # Timers
        self.delay_timer = 0
        self.sound_timer = 0
        
        # Display (64x32)
        self.display = [[0 for _ in range(64)] for _ in range(32)]
        
        # Keypad (16 keys)
        self.keypad = [0] * 16
        
        # Load font set into memory starting at 0x50
        self.font_set = [
            0xF0, 0x90, 0x90, 0x90, 0xF0,  # 0
            0x20, 0x60, 0x20, 0x20, 0x70,  # 1
            0xF0, 0x10, 0xF0, 0x80, 0xF0,  # 2
            0xF0, 0x10, 0xF0, 0x10, 0xF0,  # 3
            0x90, 0x90, 0xF0, 0x10, 0x10,  # 4
            0xF0, 0x80, 0xF0, 0x10, 0xF0,  # 5
            0xF0, 0x80, 0xF0, 0x90, 0xF0,  # 6
            0xF0, 0x10, 0x20, 0x40, 0x40,  # 7
            0xF0, 0x90, 0xF0, 0x90, 0xF0,  # 8
            0xF0, 0x90, 0xF0, 0x10, 0xF0,  # 9
            0xF0, 0x90, 0xF0, 0x90, 0x90,  # A
            0xE0, 0x90, 0xE0, 0x90, 0xE0,  # B
            0xF0, 0x80, 0x80, 0x80, 0xF0,  # C
            0xE0, 0x90, 0x90, 0x90, 0xE0,  # D
            0xF0, 0x80, 0xF0, 0x80, 0xF0,  # E
            0xF0, 0x80, 0xF0, 0x80, 0x80   # F
        ]
        
        # Load font set into memory
        for i, byte in enumerate(self.font_set):
            self.memory[0x50 + i] = byte
    
    def fetch(self):
        """Fetch instruction from memory"""
        instruction = (self.memory[self.pc] << 8) | self.memory[self.pc + 1]
        self.pc += 2
        return instruction
    
    def execute(self, instruction):
        """Execute a single instruction"""
        # Extract instruction parts
        opcode = (instruction & 0xF000) >> 12
        x = (instruction & 0x0F00) >> 8
        y = (instruction & 0x00F0) >> 4
        n = instruction & 0x000F
        nn = instruction & 0x00FF
        nnn = instruction & 0x0FFF
        
        if instruction == 0x00E0:
            # CLS - Clear display
            for row in range(32):
                for col in range(64):
                    self.display[row][col] = 0
        
        elif instruction == 0x00EE:
            # RET - Return from subroutine
            self.pc = self.stack.pop()
        
        elif opcode == 0x1:
            # JP addr - Jump to address
            self.pc = nnn
        
        elif opcode == 0x2:
            # CALL addr - Call subroutine
            self.stack.append(self.pc)
            self.pc = nnn
        
        elif opcode == 0x3:
            # SE Vx, byte - Skip if equal
            if self.V[x] == nn:
                self.pc += 2
        
        elif opcode == 0x4:
            # SNE Vx, byte - Skip if not equal
            if self.V[x] != nn:
                self.pc += 2
        
        elif opcode == 0x5:
            # SE Vx, Vy - Skip if registers equal
            if self.V[x] == self.V[y]:
                self.pc += 2
        
        elif opcode == 0x6:
            # LD Vx, byte - Load byte into register
            self.V[x] = nn
        
        elif opcode == 0x7:
            # ADD Vx, byte - Add byte to register
            self.V[x] = (self.V[x] + nn) & 0xFF
        
        elif opcode == 0x8:
            if n == 0x0:
                # LD Vx, Vy - Copy register
                self.V[x] = self.V[y]
            elif n == 0x1:
                # OR Vx, Vy - Bitwise OR
                self.V[x] |= self.V[y]
            elif n == 0x2:
                # AND Vx, Vy - Bitwise AND
                self.V[x] &= self.V[y]
            elif n == 0x3:
                # XOR Vx, Vy - Bitwise XOR
                self.V[x] ^= self.V[y]
            elif n == 0x4:
                # ADD Vx, Vy - Add with carry
                result = self.V[x] + self.V[y]
                self.V[0xF] = 1 if result > 255 else 0
                self.V[x] = result & 0xFF
            elif n == 0x5:
                # SUB Vx, Vy - Subtract with borrow
                self.V[0xF] = 1 if self.V[x] >= self.V[y] else 0
                self.V[x] = (self.V[x] - self.V[y]) & 0xFF
            elif n == 0x6:
                # SHR Vx - Shift right
                self.V[0xF] = self.V[x] & 0x1
                self.V[x] >>= 1
            elif n == 0x7:
                # SUBN Vx, Vy - Reverse subtract
                self.V[0xF] = 1 if self.V[y] >= self.V[x] else 0
                self.V[x] = (self.V[y] - self.V[x]) & 0xFF
            elif n == 0xE:
                # SHL Vx - Shift left
                self.V[0xF] = (self.V[x] & 0x80) >> 7
                self.V[x] = (self.V[x] << 1) & 0xFF
        
        elif opcode == 0x9:
            # SNE Vx, Vy - Skip if not equal
            if self.V[x] != self.V[y]:
                self.pc += 2
        
        elif opcode == 0xA:
            # LD I, addr - Load address into I
            self.I = nnn
        
        elif opcode == 0xB:
            # JP V0, addr - Jump to V0 + addr
            self.pc = nnn + self.V[0]
        
        elif opcode == 0xC:
            # RND Vx, byte - Random AND byte
            self.V[x] = random.randint(0, 255) & nn
        
        elif opcode == 0xD:
            # DRW Vx, Vy, nibble - Draw sprite
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
        
        elif opcode == 0xE:
            if nn == 0x9E:
                # SKP Vx - Skip if key pressed
                if self.keypad[self.V[x]] == 1:
                    self.pc += 2
            elif nn == 0xA1:
                # SKNP Vx - Skip if key not pressed
                if self.keypad[self.V[x]] == 0:
                    self.pc += 2
        
        elif opcode == 0xF:
            if nn == 0x07:
                # LD Vx, DT - Load delay timer
                self.V[x] = self.delay_timer
            elif nn == 0x0A:
                # LD Vx, K - Wait for key press
                key_pressed = False
                for i, key in enumerate(self.keypad):
                    if key == 1:
                        self.V[x] = i
                        key_pressed = True
                        break
                if not key_pressed:
                    self.pc -= 2  # Repeat instruction
            elif nn == 0x15:
                # LD DT, Vx - Set delay timer
                self.delay_timer = self.V[x]
            elif nn == 0x18:
                # LD ST, Vx - Set sound timer
                self.sound_timer = self.V[x]
            elif nn == 0x1E:
                # ADD I, Vx - Add to index register
                self.I += self.V[x]
            elif nn == 0x29:
                # LD F, Vx - Load font address
                self.I = 0x50 + (self.V[x] * 5)
            elif nn == 0x33:
                # LD B, Vx - Store BCD representation
                value = self.V[x]
                self.memory[self.I] = value // 100
                self.memory[self.I + 1] = (value // 10) % 10
                self.memory[self.I + 2] = value % 10
            elif nn == 0x55:
                # LD [I], Vx - Store registers
                for i in range(x + 1):
                    self.memory[self.I + i] = self.V[i]
            elif nn == 0x65:
                # LD Vx, [I] - Load registers
                for i in range(x + 1):
                    self.V[i] = self.memory[self.I + i]
    
    def cycle(self):
        """Execute one CPU cycle"""
        # Fetch instruction
        instruction = self.fetch()
        
        # Execute instruction
        self.execute(instruction)
        
        # Update timers
        if self.delay_timer > 0:
            self.delay_timer -= 1
        
        if self.sound_timer > 0:
            self.sound_timer -= 1


class TestChip8CPU:
    def setup_method(self):
        """Setup CPU for each test"""
        self.cpu = Chip8CPU()
        random.seed(42)  # Deterministic random for testing

    def test_00E0_cls(self):
        """Test CLS - Clear display"""
        # Set some pixels
        self.cpu.display[0][0] = 1
        self.cpu.display[10][20] = 1
        
        self.cpu.execute(0x00E0)
        
        # Check display is cleared
        for row in self.cpu.display:
            for pixel in row:
                assert pixel == 0

    def test_00EE_ret(self):
        """Test RET - Return from subroutine"""
        self.cpu.stack.append(0x300)
        self.cpu.execute(0x00EE)
        assert self.cpu.pc == 0x300
        assert len(self.cpu.stack) == 0

    def test_1nnn_jp_addr(self):
        """Test JP addr - Jump to address"""
        self.cpu.execute(0x1ABC)
        assert self.cpu.pc == 0xABC

    def test_2nnn_call_addr(self):
        """Test CALL addr - Call subroutine"""
        self.cpu.pc = 0x250
        self.cpu.execute(0x2ABC)
        assert self.cpu.pc == 0xABC
        assert self.cpu.stack[-1] == 0x250  # PC before increment

    def test_3xkk_se_vx_byte(self):
        """Test SE Vx, byte - Skip if equal"""
        self.cpu.V[1] = 0x55
        self.cpu.pc = 0x200
        
        # Should skip
        self.cpu.execute(0x3155)
        assert self.cpu.pc == 0x202
        
        # Should not skip
        self.cpu.pc = 0x200
        self.cpu.execute(0x3144)
        assert self.cpu.pc == 0x200

    def test_4xkk_sne_vx_byte(self):
        """Test SNE Vx, byte - Skip if not equal"""
        self.cpu.V[1] = 0x55
        self.cpu.pc = 0x200
        
        # Should skip
        self.cpu.execute(0x4144)
        assert self.cpu.pc == 0x202
        
        # Should not skip
        self.cpu.pc = 0x200
        self.cpu.execute(0x4155)
        assert self.cpu.pc == 0x200

    def test_5xy0_se_vx_vy(self):
        """Test SE Vx, Vy - Skip if registers equal"""
        self.cpu.V[1] = 0x55
        self.cpu.V[2] = 0x55
        self.cpu.pc = 0x200
        
        # Should skip
        self.cpu.execute(0x5120)
        assert self.cpu.pc == 0x202
        
        # Should not skip
        self.cpu.V[2] = 0x44
        self.cpu.pc = 0x200
        self.cpu.execute(0x5120)
        assert self.cpu.pc == 0x200

    def test_6xkk_ld_vx_byte(self):
        """Test LD Vx, byte - Load byte into register"""
        self.cpu.execute(0x6155)
        assert self.cpu.V[1] == 0x55

    def test_7xkk_add_vx_byte(self):
        """Test ADD Vx, byte - Add byte to register"""
        self.cpu.V[1] = 0x10
        self.cpu.execute(0x7120)
        assert self.cpu.V[1] == 0x30
        
        # Test overflow
        self.cpu.V[1] = 0xFF
        self.cpu.execute(0x7101)
        assert self.cpu.V[1] == 0x00

    def test_8xy0_ld_vx_vy(self):
        """Test LD Vx, Vy - Copy register"""
        self.cpu.V[2] = 0x55
        self.cpu.execute(0x8120)
        assert self.cpu.V[1] == 0x55

    def test_8xy1_or_vx_vy(self):
        """Test OR Vx, Vy - Bitwise OR"""
        self.cpu.V[1] = 0xF0
        self.cpu.V[2] = 0x0F
        self.cpu.execute(0x8121)
        assert self.cpu.V[1] == 0xFF

    def test_8xy2_and_vx_vy(self):
        """Test AND Vx, Vy - Bitwise AND"""
        self.cpu.V[1] = 0xF0
        self.cpu.V[2] = 0x0F
        self.cpu.execute(0x8122)
        assert self.cpu.V[1] == 0x00

    def test_8xy3_xor_vx_vy(self):
        """Test XOR Vx, Vy - Bitwise XOR"""
        self.cpu.V[1] = 0xF0
        self.cpu.V[2] = 0x0F
        self.cpu.execute(0x8123)
        assert self.cpu.V[1] == 0xFF

    def test_8xy4_add_vx_vy(self):
        """Test ADD Vx, Vy - Add with carry"""
        self.cpu.V[1] = 0x10
        self.cpu.V[2] = 0x20
        self.cpu.execute(0x8124)
        assert self.cpu.V[1] == 0x30
        assert self.cpu.V[0xF] == 0
        
        # Test carry
        self.cpu.V[1] = 0xFF
        self.cpu.V[2] = 0x01
        self.cpu.execute(0x8124)
        assert self.cpu.V[1] == 0x00
        assert self.cpu.V[0xF] == 1

    def test_8xy5_sub_vx_vy(self):
        """Test SUB Vx, Vy - Subtract with borrow"""
        self.cpu.V[1] = 0x30
        self.cpu.V[2] = 0x20
        self.cpu.execute(0x8125)
        assert self.cpu.V[1] == 0x10
        assert self.cpu.V[0xF] == 1
        
        # Test borrow
        self.cpu.V[1] = 0x20
        self.cpu.V[2] = 0x30
        self.cpu.execute(0x8125)
        assert self.cpu.V[1] == 0xF0  # 0x20 - 0x30 = -0x10 = 0xF0
        assert self.cpu.V[0xF] == 0

    def test_8xy6_shr_vx(self):
        """Test SHR Vx - Shift right"""
        self.cpu.V[1] = 0x05  # Binary: 101
        self.cpu.execute(0x8126)
        assert self.cpu.V[1] == 0x02  # Binary: 10
        assert self.cpu.V[0xF] == 1  # LSB was 1

    def test_8xy7_subn_vx_vy(self):
        """Test SUBN Vx, Vy - Reverse subtract"""
        self.cpu.V[1] = 0x20
        self.cpu.V[2] = 0x30
        self.cpu.execute(0x8127)
        assert self.cpu.V[1] == 0x10
        assert self.cpu.V[0xF] == 1
        
        # Test borrow
        self.cpu.V[1] = 0x30
        self.cpu.V[2] = 0x20
        self.cpu.execute(0x8127)
        assert self.cpu.V[1] == 0xF0  # 0x20 - 0x30 = -0x10 = 0xF0
        assert self.cpu.V[0xF] == 0

    def test_8xyE_shl_vx(self):
        """Test SHL Vx - Shift left"""
        self.cpu.V[1] = 0x82  # Binary: 10000010
        self.cpu.execute(0x812E)
        assert self.cpu.V[1] == 0x04  # Binary: 00000100
        assert self.cpu.V[0xF] == 1  # MSB was 1

    def test_9xy0_sne_vx_vy(self):
        """Test SNE Vx, Vy - Skip if not equal"""
        self.cpu.V[1] = 0x55
        self.cpu.V[2] = 0x44
        self.cpu.pc = 0x200
        
        # Should skip
        self.cpu.execute(0x9120)
        assert self.cpu.pc == 0x202
        
        # Should not skip
        self.cpu.V[2] = 0x55
        self.cpu.pc = 0x200
        self.cpu.execute(0x9120)
        assert self.cpu.pc == 0x200

    def test_Annn_ld_i_addr(self):
        """Test LD I, addr - Load address into I"""
        self.cpu.execute(0xAABC)
        assert self.cpu.I == 0xABC

    def test_Bnnn_jp_v0_addr(self):
        """Test JP V0, addr - Jump to V0 + addr"""
        self.cpu.V[0] = 0x10
        self.cpu.execute(0xB200)
        assert self.cpu.pc == 0x210

    def test_Cxkk_rnd_vx_byte(self):
        """Test RND Vx, byte - Random AND byte"""
        random.seed(42)
        self.cpu.execute(0xC1FF)
        # With seed 42, first random should be 57
        assert self.cpu.V[1] == 57  # 57 & 0xFF

    def test_Dxyn_drw_vx_vy_nibble(self):
        """Test DRW Vx, Vy, nibble - Draw sprite"""
        self.cpu.V[1] = 10  # x position
        self.cpu.V[2] = 5   # y position
        self.cpu.I = 0x300
        self.cpu.memory[0x300] = 0xF0  # Top row of sprite
        
        self.cpu.execute(0xD121)  # Draw 1-line sprite
        
        # Check pixels were set
        assert self.cpu.display[5][10] == 1
        assert self.cpu.display[5][11] == 1
        assert self.cpu.display[5][12] == 1
        assert self.cpu.display[5][13] == 1
        assert self.cpu.V[0xF] == 0  # No collision

    def test_Ex9E_skp_vx(self):
        """Test SKP Vx - Skip if key pressed"""
        self.cpu.V[1] = 0x5
        self.cpu.keypad[0x5] = 1
        self.cpu.pc = 0x200
        
        # Should skip
        self.cpu.execute(0xE19E)
        assert self.cpu.pc == 0x202

    def test_ExA1_sknp_vx(self):
        """Test SKNP Vx - Skip if key not pressed"""
        self.cpu.V[1] = 0x5
        self.cpu.keypad[0x5] = 0
        self.cpu.pc = 0x200
        
        # Should skip
        self.cpu.execute(0xE1A1)
        assert self.cpu.pc == 0x202

    def test_Fx07_ld_vx_dt(self):
        """Test LD Vx, DT - Load delay timer"""
        self.cpu.delay_timer = 0x30
        self.cpu.execute(0xF107)
        assert self.cpu.V[1] == 0x30

    def test_Fx0A_ld_vx_k(self):
        """Test LD Vx, K - Wait for key press"""
        self.cpu.pc = 0x200
        self.cpu.keypad[0x5] = 1
        self.cpu.execute(0xF10A)
        assert self.cpu.V[1] == 0x5
        assert self.cpu.pc == 0x200  # PC not decremented because key was pressed

    def test_Fx15_ld_dt_vx(self):
        """Test LD DT, Vx - Set delay timer"""
        self.cpu.V[1] = 0x30
        self.cpu.execute(0xF115)
        assert self.cpu.delay_timer == 0x30

    def test_Fx18_ld_st_vx(self):
        """Test LD ST, Vx - Set sound timer"""
        self.cpu.V[1] = 0x30
        self.cpu.execute(0xF118)
        assert self.cpu.sound_timer == 0x30

    def test_Fx1E_add_i_vx(self):
        """Test ADD I, Vx - Add to index register"""
        self.cpu.I = 0x200
        self.cpu.V[1] = 0x50
        self.cpu.execute(0xF11E)
        assert self.cpu.I == 0x250

    def test_Fx29_ld_f_vx(self):
        """Test LD F, Vx - Load font address"""
        self.cpu.V[1] = 0xA
        self.cpu.execute(0xF129)
        assert self.cpu.I == 0x50 + (0xA * 5)  # Font address for 'A'

    def test_Fx33_ld_b_vx(self):
        """Test LD B, Vx - Store BCD representation"""
        self.cpu.V[1] = 123
        self.cpu.I = 0x300
        self.cpu.execute(0xF133)
        assert self.cpu.memory[0x300] == 1
        assert self.cpu.memory[0x301] == 2
        assert self.cpu.memory[0x302] == 3

    def test_Fx55_ld_i_vx(self):
        """Test LD [I], Vx - Store registers"""
        self.cpu.V[0] = 0x10
        self.cpu.V[1] = 0x20
        self.cpu.V[2] = 0x30
        self.cpu.I = 0x300
        self.cpu.execute(0xF255)  # Store V0-V2
        assert self.cpu.memory[0x300] == 0x10
        assert self.cpu.memory[0x301] == 0x20
        assert self.cpu.memory[0x302] == 0x30

    def test_Fx65_ld_vx_i(self):
        """Test LD Vx, [I] - Load registers"""
        self.cpu.memory[0x300] = 0x10
        self.cpu.memory[0x301] = 0x20
        self.cpu.memory[0x302] = 0x30
        self.cpu.I = 0x300
        self.cpu.execute(0xF265)  # Load V0-V2
        assert self.cpu.V[0] == 0x10
        assert self.cpu.V[1] == 0x20
        assert self.cpu.V[2] == 0x30

    def test_cycle(self):
        """Test complete CPU cycle"""
        # Load a simple program: LD V1, 0x55
        self.cpu.memory[0x200] = 0x61
        self.cpu.memory[0x201] = 0x55
        
        self.cpu.cycle()
        
        assert self.cpu.V[1] == 0x55
        assert self.cpu.pc == 0x202

    def test_timer_decrement(self):
        """Test that timers decrement during cycles"""
        self.cpu.delay_timer = 10
        self.cpu.sound_timer = 5
        
        # Load NOP instruction
        self.cpu.memory[0x200] = 0x00
        self.cpu.memory[0x201] = 0xE0  # CLS
        
        self.cpu.cycle()
        
        assert self.cpu.delay_timer == 9
        assert self.cpu.sound_timer == 4


if __name__ == "__main__":
    pytest.main([__file__])