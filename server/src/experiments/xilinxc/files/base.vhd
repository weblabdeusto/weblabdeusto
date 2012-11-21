------------------------------------------------------------------------------------
---- Company: 
---- Engineer: 
---- 
---- Create Date:    07:59:54 10/01/2012 
---- Design Name: 
---- Module Name:    prueba - Behavioral 
---- Project Name: 
---- Target Devices: 
---- Tool versions: 
---- Description: 
----
---- Dependencies: 
----
---- Revision: 
---- Revision 0.01 - File Created
---- Additional Comments: 
----
------------------------------------------------------------------------------------
--library IEEE;
--use IEEE.STD_LOGIC_1164.ALL;
--
---- Uncomment the following library declaration if using
---- arithmetic functions with Signed or Unsigned values
----use IEEE.NUMERIC_STD.ALL;
--
---- Uncomment the following library declaration if instantiating
---- any Xilinx primitives in this code.
----library UNISIM;
----use UNISIM.VComponents.all;
--
--entity prueba is
--port(
--swt: in std_logic_vector (7 downto 0);
--btn: in std_logic_vector (3 downto 0);
--led: out std_logic_vector (7 downto 0);
--an: out std_logic_vector (3 downto 0);
--segmentos: out std_logic_vector (6 downto 0);
--punto: out std_logic
--);
--
--end prueba;
--
--architecture Behavioral of prueba is
--
--begin
--
--an<=swt(7)&swt(7)&swt(7)&swt(7);
--segmentos<=swt(6 downto 0);
--punto<=btn(3);
--led<=btn(2)&btn(2)&btn(2)&btn(2)&btn(1)&btn(1)&btn(1)&(not(btn(0)));
--
--end Behavioral;

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.STD_LOGIC_ARITH.ALL;
use IEEE.STD_LOGIC_UNSIGNED.ALL;

entity Untitled is
	Port (
		inicio: in std_logic;
		ck: in std_logic;
		I0: in std_logic;
		O0: out std_logic
		);
end Untitled;

architecture behavioral of Untitled is

type nombres_estados is (Q0);
signal estado: nombres_estados;
signal entrada_aux: std_logic;

begin

entrada_aux<=I0;

process(inicio, ck)
begin
if inicio='1' then
	estado<=Q0;
elsif ck='1' and ck'event then
	case estado is
		when Q0 =>
			case  entrada_aux is
				when others => estado<=Q0;
			end case;
		when others => estado<=Q0;
	end case;
end if;
end process;

process(estado)
begin
case estado is
	when Q0 =>
		O0<='1';
end case;
end process;

end behavioral;

