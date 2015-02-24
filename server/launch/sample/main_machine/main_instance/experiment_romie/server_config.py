# -*- coding: utf-8 -*-

import os

romie_sqlite = os.path.join(CURRENT_PATH, "forotech.db")

questions = [
	[ # 0 difficulty
		{
			"question": '¿Qué espectro de ondas electromagnéticas usan las radiografías?',
			"answers": [
				'Rayos gamma',
				'Rayos X',
				'Ondas de radio'
			],
			"correct": 1,
			"points": 55,
			"time": 20
		},
		{
			"question": '¿Cuántos huesos tiene el ser humano?',
			"answers": [
				128,
				204,
				233,
				206
			],
			"correct": 3,
			"points": 65,
			"time": 25
		}
	],
	[ # 1 difficulty
		{
			"question": '¿Cuántas horas tiene el 29 de febrero de un año visiesto?',
			"answers": [
				23.5,
				24,
				24.5
			],
			"correct": 1,
			"points": 70,
			"time": 20
		},
		{
			"question": '¿En qué año se descubrió América?',
			"answers": [
				1465,
				1523,
				1492,
				1812
			],
			"correct": 2,
			"points": 85,
			"time": 25
		},
		{
			"question": '¿Qué miembro de una orquesta puede dar la espalda en un concierto?',
			"answers": [
				'El batería',
				'El arpa',
				'El violín',
				'El director'
			],
			"correct": 3,
			"points": 80,
			"time": 22
		}
	],
	[ # 2 difficulty
		{
			"question": '¿Cómo se llaman los naturales de Huesca?',
			"answers": [
				'Huescanos',
				'Oscenses',
				'Huescenses',
				'De Huesca'
			],
			"correct": 1,
			"points": 105,
			"time": 25
		},
		{
			"question": '¿Qué mide el número pi (π)?',
			"answers": [
				'La relación entre el diámetro y la superficie de un círculo',
				'La relación entre el radio y el diámetro de un círculo',
				'La relación entre un cuadrado y un círculo',
				'La relación entre el diámetro y la circunferencia de un círculo'
			],
			"correct": 3,
			"points": 115,
			"time": 20
		}
	],
	[ # 3 difficulty
		{
			"question": '¿Cuáles son las siglas en inglés para el término OVNI?',
			"answers": [
				'ET',
				'OVNI',
				'UFO',
				'EIL'
			],
			"correct": 2,
			"points": 135,
			"time": 25
		},
		{
			"question": '¿Qué mide una pinta?',
			"answers": [
				'El volumen',
				'La masa',
				'La fuerza',
				'No hay ninguna medida llamada pinta'
			],
			"correct": 0,
			"points": 140,
			"time": 24
		}
	],
	[ # 4 difficulty
		{
			"question": '¿Cuántas provincias gallegas limitan con Portugal?',
			"answers": [
				'Ninguna',
				1,
				2,
				3
			],
			"correct": 2,
			"points": 155,
			"time": 20
		},
		{
			"question": '¿Cuáles son las células encargadas de destruir los virus en nuestro organismo?',
			"answers": [
				'Los glóbulos blancos',
				'Los anticuerpos',
				'Las neuronas',
				'Los góbulos rojos'
			],
			"correct": 0,
			"points": 165,
			"time": 25
		}
	],
	[ # 5 difficulty
		{
			"question": '¿En qué año se creó el ordenador personal Apple I?',
			"answers": [
				1834,
				1954,
				1976,
				1994
			],
			"correct": 2,
			"points": 195,
			"time": 24
		},
		{
			"question": '¿En qué año llegaron los seres humanos a la Luna?',
			"answers": [
				'Nunca han llegado seres humanos a la Luna',
				1468,
				1969,
				2005
			],
			"correct": 2,
			"points": 205,
			"time": 25
		}
	],
	[ # 6 difficulty
		{
			"question": '¿En qué año nació Alan Turing, creador del primer ordenador de la historia?',
			"answers": [
				1876,
				1912,
				1945,
				1987
			],
			"correct": 1,
			"points": 225,
			"time": 25
		}
	],
	[ # 7 difficulty
		{
			"question": '¿Cual fue el último y más poderoso lider de los Hunos?',
			"answers": [
				'Anibal',
				'Atila',
				'Julio Cesar',
				'Joffrey Baratheon'
			],
			"correct": 1,
			"points": 215,
			"time": 20
		}
	],
	[ # 8 difficulty
		{
			"question": '¿En qué provincia española están las ruinas de Numancia?',
			"answers": [
				'Palencia',
				'Segovia',
				'Ávila',
				'Burgos'
			],
			"correct": 0,
			"points": 255,
			"time": 20
		}
	],
	[ # 9 difficulty
		{
			"question": '¿Quién fue el primero en usar la letra griega pi (π) para el número 3,141592653...?',
			"answers": [
				'Leonhard Euler',
				'Alan Turing',
				'William Jones',
				'William Oughtred'
			],
			"correct": 3,
			"points": 314,
			"time": 31
		}
	],
	[ # 10 difficulty
		{
			"question": '¿Cuánto dura la incubación de un huevo de emu?',
			"answers": [
				'Aproximadamente 52 días',
				'Aproximadamente 23 días',
				'Aproximadamente 76 días',
				'Aproximadamente 92 días'
			],
			"correct": 0,
			"points": 340,
			"time": 20
		}
	],
]
