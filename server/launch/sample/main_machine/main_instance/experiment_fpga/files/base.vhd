-- @@@CLOCK:WEBLAB@@@
library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.STD_LOGIC_ARITH.ALL;
use IEEE.STD_LOGIC_UNSIGNED.ALL;

entity base is
	Port (
		
		inicio : in std_logic;
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
		
                                        swi9 : in std_logic;
                                        vleds : out std_logic_vector (7 downto 0)
                                
		);
end base;

architecture behavioral of base is


begin
led0 <= swi6;
led1 <= swi5;
led2 <= swi4;
led3 <= swi3;


                                        vleds(0) <= led7;
                                        vleds(1) <= led6;
                                        vleds(2) <= led5;
                                        vleds(3) <= led4;
                                        vleds(4) <= led3;
                                        vleds(5) <= led2;
                                        vleds(6) <= led1;
                                        vleds(7) <= led0;
                                        
                                end behavioral
                                ;
