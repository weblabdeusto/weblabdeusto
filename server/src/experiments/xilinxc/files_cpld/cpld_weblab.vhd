----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date:    09:09:46 09/20/2013 
-- Design Name: 
-- Module Name:    cpld_weblab - Behavioral 
-- Project Name: 
-- Target Devices: 
-- Tool versions: 
-- Description: 
--
-- Dependencies: 
--
-- Revision: 
-- Revision 0.01 - File Created
-- Additional Comments: 
--
----------------------------------------------------------------------------------
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

-- Uncomment the following library declaration if using
-- arithmetic functions with Signed or Unsigned values
--use IEEE.NUMERIC_STD.ALL;

-- Uncomment the following library declaration if instantiating
-- any Xilinx primitives in this code.
--library UNISIM;
--use UNISIM.VComponents.all;

entity cpld_weblab is
port(
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
end cpld_weblab;

architecture Behavioral of cpld_weblab is
begin
	led0 <= swi0;
end Behavioral;

