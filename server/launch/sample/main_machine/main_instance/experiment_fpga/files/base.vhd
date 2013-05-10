library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.STD_LOGIC_ARITH.ALL;
use IEEE.STD_LOGIC_UNSIGNED.ALL;

entity base is
	Port (
		clk : in std_logic;

		led0 : inout std_logic;
		led1 : inout std_logic;
		led2 : inout std_logic;
		led3 : inout std_logic;
		led4 : inout std_logic;
		led5 : inout std_logic;
		led6 : inout std_logic;
		led7 : inout std_logic;

		ena0 : inout std_logic;
		ena1 : inout std_logic;
		ena2 : inout std_logic;
		ena3 : inout std_logic;

		seg0 : inout std_logic;
		seg1 : inout std_logic;
		seg2 : inout std_logic;
		seg3 : inout std_logic;
		seg4 : inout std_logic;
		seg5 : inout std_logic;
		seg6 : inout std_logic;

		dot : inout std_logic;

		but0 : in std_logic;
		but1 : in std_logic;
		but2 : in std_logic;
		but3 : in std_logic;

		swi0 : in std_logic;
		swi1 : in std_logic;
		swi2 : in std_logic;
		swi3 : in std_logic;
		swi4 : in std_logic;
		swi5 : in std_logic;
		swi6 : in std_logic;
		swi7 : in std_logic;
		swi8 : in std_logic;
		swi9 : in std_logic
		);
end base;

architecture behavioral of base is
begin
	led0<='0';
	led1<=((not(swi0) and swi1 and not(swi3)) or (not(swi0) and swi1 and not(swi2)));
	led2<=((not(swi0) and not(swi1) and swi2));
	led3<=((not(swi0) and not(swi1) and swi3));
end behavioral;
