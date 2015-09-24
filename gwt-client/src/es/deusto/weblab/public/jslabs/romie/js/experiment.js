var experiment = {
  code : "x148a",
  experimentName : "Tarea de Cartas",
  year : "2015",
  developers : ["Tomás de la Vega","Helena Matute","Fernando Blanco"],
  mode : "online",
  language : "es",
  subjectID : Math.floor((Math.random() * 1000000) + 1),
  group : Math.floor((Math.random() * 2) + 1),
  balance : Math.floor((Math.random() * 2) + 1),
  age : 0,
  sex : 0,
  course : "",
  user : "",
  currentIndex : 0,
  currentState : 0,
  currentPhase : 0,
  width : screen.availWidth,
  height : screen.availHeight,
  phases : [[],[]],
  intervencion : [[],[]],
  juicios : [{question : '', response : 0},{question : '', response : 0}],
  screens : [
    {
      id : 'intro',
      state : 0,
      backState : 0,
      nextState : 1,
      cabecera : 'Tarea de Cartas',
      contenido : '<p class="text-center">(Software para psicología Experimental)<br>Versión 1,0, Español 2015<br>http://www.labpsico.com<br><a id="ref" href="#" onclick="hideAndShowReferences()">Créditos, Copyright y Artículos en los que se describe este programa</a></p><p id="references"></p>',
      btnBack : '',
      btnNext : 'Continuar',
      showBtnBack : false,
      showBtnNext : true
    },
    {
      id : 'etica',
      State : 1,
      backState : 0,
      nextState : 3,
      cabecera : 'Tu Participación es Anónima y Voluntaria',
      contenido : 'Antes de nada queremos agradecer tu participación en este experimento, ya que sin la colaboración de personas como tú no sería posible esta investigación.<br>Debes saber que en esta tarea no hay respuestas buenas ni malas. Lo que queremos estudiar son los mecanismos psicológicos básicos que se dan en todas las personas. Para ello, necesitamos que, si deseas participar, lo hagas con el mayor interés. No tienes que identificarte, y los datos que nos aportes se unirán a los del total del grupo y serán analizados estadísticamente. Tú participación es voluntaria y anónima.<br>Si tras haber leído el mensaje deseas continuar, pulsa en el botón \'Continuar\'.',
      btnBack : 'Atrás',
      btnNext : 'Continuar',
      showBtnBack : true,
      showBtnNext : true
    },
    {
      id : 'info',
      state : 2,
      backState : 1,
      nextState : 3,
      cabecera : 'Datos',
      contenido : '<div class="col-md-6"><form name="formulario" id="formulario"><strong>SEXO</strong>: <select class="form-control" name="sexo" id="sexo"><option value="Hombre">Hombre</option><option value="Mujer">Mujer</option></select><strong>EDAD</strong>:<input class="form-control" type="text" id="edad" name="edad" maxlength="2"><strong>CURSO: </strong><input class="form-control" type="text" name="curso" id="curso"><strong>USUARIO WEBLAB DEUSTO: </strong><input class="form-control" type="text" name="user" id="user"><br><button type="button" class="btn btn-primary btn-lg buttons" onclick="validate()">Continuar</button></form></div>',
      btnBack : 'Atrás',
      btnNext : 'Continuar',
      showBtnBack : true,
      showBtnNext : false
    },
    {
      id : 'instrucciones1',
      state : 3,
      backState: 1,
      nextState: 4,
      cabecera : 'Instrucciones',
      contenido : '',
      btnBack : 'Atrás',
      btnNext : 'Continuar',
      showBtnBack : false,
      showBtnNext : true
    },
    {
      id : 'fase1',
      state : 4,
      backState: 3,
      nextState: 5,
      cabecera : '',
      contenido : '',
      btnBack : 'Atrás',
      btnNext : 'Continuar',
      showBtnBack : false,
      showBtnNext : false
    },
    {
      id : 'juicio1',
      state : 5,
      backState: 4,
      nextState: 6,
      cabecera : 'Juicio',
      contenido : '',
      btnBack : 'Atrás',
      btnNext : 'Continuar',
      showBtnBack : false,
      showBtnNext : true
    },
    {
      id : 'intervencíon1',
      state : 6,
      backState: 5,
      nextState: 7,
      cabecera : 'Intervención',
      contenido : '',
      btnBack : 'Atrás',
      btnNext : 'Continuar',
      showBtnBack : false,
      showBtnNext : true
    },
    {
      id : 'instrucciones2',
      state : 7,
      backState: 6,
      nextState: 8,
      cabecera : 'Instrucciones',
      contenido : '',
      btnBack : 'Atrás',
      btnNext : 'Continuar',
      showBtnBack : false,
      showBtnNext : true
    },
    {
      id : 'fase2',
      state : 8,
      backState: 7,
      nextState: 9,
      cabecera : '',
      contenido : '',
      btnBack : 'Atrás',
      btnNext : 'Continuar',
      showBtnBack : false,
      showBtnNext : false
    },
    {
      id : 'juicio2',
      state : 9,
      backState: 8,
      nextState: 10,
      cabecera : 'Juicio',
      contenido : '',
      btnBack : 'Atrás',
      btnNext : 'Continuar',
      showBtnBack : false,
      showBtnNext : true
    },
    {
      id : 'intervencíon2',
      state : 10,
      backState: 9,
      nextState: 11,
      cabecera : 'Intervención',
      contenido : '',
      btnBack : 'Atrás',
      btnNext : 'Continuar',
      showBtnBack : false,
      showBtnNext : true
    },
    {
      id : 'enviarDatos',
      state : 11,
      backState: 12,
      nextState: 12,
      cabecera : 'Enviar Datos',
      contenido : 'A continuación podrás enviar los resultados para que se incluyan en nuestro estudio, los datos que nos aportes se unirán a los del grupo y serán analizados estadísticamente. Para hacerlo haz click en el botón \"Enviar\". Si por alguna razón no deseas enviarnóslos haz click en el botón \"Cancelar\".',
      btnBack : 'Cancelar',
      btnNext : 'Enviar',
      showBtnBack : true,
      showBtnNext : true
    },
    {
      id : 'Fin',
      state : 12,
      backState: 12,
      nextState: 12,
      cabecera : 'Gracias',
      contenido : 'Gracias por participar en el experimento.<br><button id="siguiente" data-role="none" type="button" class="buttons" onclick="nextExperiment()">Siguiente</button>',
      btnBack : 'Cancelar',
      btnNext : 'Enviar',
      showBtnBack : false,
      showBtnNext : false
    }
  ],
  decCurrentState : function() {this.currentState = this.screens[this.currentState].backState;},
  addCurrentState : function() {this.currentState = this.screens[this.currentState].nextState;},
  addCurrentIndex : function() {this.currentIndex++;},
  addCurrentPhase : function() {this.currentPhase++;},
  resetCurrentIndex : function() {this.currentIndex = 0;},
  loadPhases : function(){
    var i,instrucciones1,instrucciones2,key1,key2,nokey1,nokey2,outcome1,outcome2,nootcome1,nooutcome2,question1,question2,juicio1,juicio2;
    instrucciones1 = 'En este juego verás unas cartas con el dorso de color violeta.<br> Algunas cartas tienen una marca con forma de una equis roja.<br>Además, algunas cartas esconden una cara sonriente por el otro lado.<br>Cada vez que aparazeca una carta podrás darle la vuelta, pero antes te preguntaremos si crees que el muñeco sonriente estará en el otro lado.<br>Después te daremos la vuelta a la carta y verás si está o no la cara sonriente.<br>Tu misión es averiguar si las marcas sirven para saber cuándo va aparecer la cara sonriente.'
    instrucciones2 = 'En este juego verás unas cartas con el dorso de color naranja.<br> Algunas cartas tienen una marca con forma de una estrella negra.<br>Además, algunas cartas esconden un sol por el otro lado.<br>Cada vez que aparazeca una carta podrás darle la vuelta, pero antes te preguntaremos si crees que el muñeco sonriente estará en el otro lado.<br>Después te daremos la vuelta a la carta y verás si está o no el sol.<br>Tu misión es averiguar si las marcas sirven para saber cuándo va aparecer el sol.'
    juicio1 = '¿Hasta qué punto crees que la marca de las cartas sirve para saber cuándo va aparecer la cara sonriente?<br>0: No sirve para nada; 50: Sirve a medias; 100: Sirve perfectamente.';
    juicio2 = '¿Hasta qué punto crees que la marca de las cartas sirve para saber cuándo va aparecer el sol?<br>0: No sirve para nada; 50: Sirve a medias; 100: Sirve perfectamente.'
    //Intervención
    if(this.group === 1){
      //intervención 1 medicinas
      this.intervencion[0].push({contenido : 'A continuación PODRÁS LEER UNA INFORMACIÓN que te servirá de gran ayuda en los siguientes niveles. Léelo despacio y entiéndelo bien, ¿de acuerdo?.<br>'});
      this.intervencion[0].push({contenido : '¿Cómo saber si funciona una medicina para curar el dolor de cabeza?<br>Para saber si funciona, necesitamos COMPARAR dos informaciones:<br><img class="center-block img-responsive" src="img/intervencion/Intervencion1.png"></img><br>'});
      this.intervencion[0].push({contenido : 'En el siguiente ejemplo, la medicina parece funcionar: de los que toman el tratamiento, se curan muchos, y de los que no lo toman, se curan pocos.<br><img class="center-block img-responsive" src="img/intervencion/Intervencion2.png"></img><br>'});
      this.intervencion[0].push({contenido : 'Sin embargo, la siguiente medicina parece que no funciona, ya que se cura aproximadamente el mismo porcentaje de gente tomando la medicina que sin tomarla.<br><img class="center-block img-responsive" src="img/intervencion/Intervencion3.png"></img><br>'});
      this.intervencion[0].push({contenido : 'Conclusiones de lo que hemos aprendido:<br>-No sólo importa cuánta gente se cura tras tomar el tratamiento. Debemos comparar ese porcentaje con el de la gente que se cura SIN tomar el tratamiento.<br>-Muchas veces la publicidad y los medios sólo nos enseñan una de las dos informaciones necesarias. Por ejemplo, cuando nos dicen: "Ocho de cada diez clientes se siente mejor tras probar nuestro producto". Este dato es engañoso porque no sabemos cuántas personas que no usan el producto también se sentirían mejor (por ejemplo usando un producto de la competencia o incluso tras dormir unas horas). ¡Hay que estar alerta para que los anunciantes no nos engañen! Y para ello, hay que obtener toda la información que necesitamos y compararla como hemos visto.<br>'});
      //intervención 2 estrellas
      this.intervencion[1].push({contenido : 'Como las personas, las estrellas nacen, crecen y mueren. Sus lugares de nacimiento son enormes nubes frías formadas por gas y polvo, conocidas como "nebulosas". Estas nubes comienzan a encogerse por obra de su propia gravedad.<br><img class="center-block img-responsive" src="img/intervencion/intervencion2-1.png"></img><br>'});
      this.intervencion[1].push({contenido : 'A medida que una nube pierde tamaño, se fragmenta en grupos más pequeños. Cada fragmento puede finalmente volverse tan caliente y denso que se inica una reacción nuclear. Cuando la temperatura alcanza los 10 millones de grados, el fragmento se coniverte en una nueva estrella.<br><img class="center-block img-responsive" src="img/intervencion/intervencion2-2.png"></img><br>'});
      this.intervencion[1].push({contenido : 'Tras su nacimiento, la mayoría de las nuevas estrellas se encuentran situada en el centro de un disco plano de gas y polvo. Gran parte del gas y polvo acaba siendo barrida por la radiación estelar. Sin embargo, antes de que esto ocurra, pueden formarse planetas alrededor de la estrella central.<br>Los vehículos espaciales como el Observatorio Espacial de Infrarrojos (ISO) de la ESA, son capaces de detectar el calor proveniente de estrellas y planetas invisibles que se están formando en el interior de esas nubes.<br>'});
    }else {
      //intervención 1 estrellas
      this.intervencion[0].push({contenido : 'A continuación PODRÁS LEER UNA INFORMACIÓN que te servirá de gran ayuda en los siguientes niveles. Léelo despacio y entiéndelo bien, ¿de acuerdo?.<br>'});
      this.intervencion[0].push({contenido : 'Como las personas, las estrellas nacen, crecen y mueren. Sus lugares de nacimiento son enormes nubes frías formadas por gas y polvo, conocidas como "nebulosas". Estas nubes comienzan a encogerse por obra de su propia gravedad.<br><img src="img/intervencion/intervencion2-1.png" class="center-block img-responsive"></img><br>'});
      this.intervencion[0].push({contenido : 'A medida que una nube pierde tamaño, se fragmenta en grupos más pequeños. Cada fragmento puede finalmente volverse tan caliente y denso que se inica una reacción nuclear. Cuando la temperatura alcanza los 10 millones de grados, el fragmento se coniverte en una nueva estrella.<br><img class="center-block img-responsive" src="img/intervencion/intervencion2-2.png"></img><br>'});
      this.intervencion[0].push({contenido : 'Tras su nacimiento, la mayoría de las nuevas estrellas se encuentran situada en el centro de un disco plano de gas y polvo. Gran parte del gas y polvo acaba siendo barrida por la radiación estelar. Sin embargo, antes de que esto ocurra, pueden formarse planetas alrededor de la estrella central.<br>Los vehículos espaciales como el Observatorio Espacial de Infrarrojos (ISO) de la ESA, son capaces de detectar el calor proveniente de estrellas y planetas invisibles que se están formando en el interior de esas nubes.<br>'});
      //intervención 2 medicinas
      this.intervencion[1].push({contenido : '¿Cómo saber si funciona una medicina para curar el dolor de cabeza?<br>Para saber si funciona, necesitamos COMPARAR dos informaciones:<br><img class="center-block img-responsive" src="img/intervencion/Intervencion1.png"></img><br>'});
      this.intervencion[1].push({contenido : 'En el siguiente ejemplo, la medicina parece funcionar: de los que toman el tratamiento, se curan muchos, y de los que no lo toman, se curan pocos.<br><img class="center-block img-responsive" src="img/intervencion/Intervencion2.png"></img><br>'});
      this.intervencion[1].push({contenido : 'Sin embargo, la siguiente medicina parece que no funciona, ya que se cura aproximadamente el mismo porcentaje de gente tomando la medicina que sin tomarla.<br><img class="center-block img-responsive" src="img/intervencion/Intervencion3.png"></img><br>'});
      this.intervencion[1].push({contenido : 'Conclusiones de lo que hemos aprendido:<br>-No sólo importa cuánta gente se cura tras tomar el tratamiento. Debemos comparar ese porcentaje con el de la gente que se cura SIN tomar el tratamiento.<br>-Muchas veces la publicidad y los medios sólo nos enseñan una de las dos informaciones necesarias. Por ejemplo, cuando nos dicen: "Ocho de cada diez clientes se siente mejor tras probar nuestro producto". Este dato es engañoso porque no sabemos cuántas personas que no usan el producto también se sentirían mejor (por ejemplo usando un producto de la competencia o incluso tras dormir unas horas). ¡Hay que estar alerta para que los anunciantes no nos engañen! Y para ello, hay que obtener toda la información que necesitamos y compararla como hemos visto.<br>'});
    }
    if(this.balance === 1){
      this.juicios[0].question = juicio1;
      this.juicios[1].question = juicio2;
      question1 = '¿Crees que hay una cara sonriente al otro lado?';
      question2 = '¿Crees que hay un sol al otro lado?';
      this.screens[3].contenido = instrucciones1;
      this.screens[7].contenido = instrucciones2;
      key1 = 'img/CueBaraja1.png';
      key2 = 'img/CueBaraja2.png';
      nokey1 = 'img/noCueBaraja1.png';
      nokey2 = 'img/noCueBaraja2.png';
      outcome1 = 'img/OutcomeBaraja1.png';
      outcome2 = 'img/OutcomeBaraja2.png';
      nootcome1 = 'img/noOutcomeBaraja1.png';
      nooutcome2 = 'img/noOutcomeBaraja2.png';
    }else{
      this.juicios[0].question = juicio2;
      this.juicios[1].question = juicio1;
      question2 = '¿Crees que hay una cara sonriente al otro lado?';
      question1 = '¿Crees que hay un sol al otro lado?';
      this.screens[7].contenido = instrucciones1;
      this.screens[3].contenido = instrucciones2;
      key1 = 'img/CueBaraja2.png';
      key2 = 'img/CueBaraja1.png';
      nokey1 = 'img/noCueBaraja2.png';
      nokey2 = 'img/noCueBaraja1.png';
      outcome1 = 'img/OutcomeBaraja2.png';
      outcome2 = 'img/OutcomeBaraja1.png';
      nootcome1 = 'img/noOutcomeBaraja2.png';
      nooutcome2 = 'img/noOutcomeBaraja1.png';
    }
    //insertar ensayos tipo a y c
    for(i=0;i<15;i++){
      //Fase1
      this.phases[0].push({type : 'a',key : key1,outcome : outcome1,response : 0,question : question1});
      this.phases[0].push({type : 'c',key : nokey1,outcome : outcome1,response : 0,question : question1});
      //Fase2
      this.phases[1].push({type : 'a',key : key2,outcome : outcome2,response : 0,question : question2});
      this.phases[1].push({type : 'c',key : nokey2,outcome : outcome2,response : 0,question : question2});
    }
    //insertar ensayos tipo b y d
    for(i=0;i<5;i++){
      //Fase1
      this.phases[0].push({type : 'b',key : key1,outcome : nootcome1,response : 0,question : question1});
      this.phases[0].push({type : 'd',key : nokey1,outcome : nootcome1,response : 0,question : question1});
      //Fase2
      this.phases[1].push({type : 'b',key : key2,outcome : nooutcome2,response : 0,question : question2});
      this.phases[1].push({type : 'd',key : nokey2,outcome : nooutcome2,response : 0,question : question2});
    }
    //aleatorizar secuencias
    fisherYates(this.phases[0]);
    fisherYates(this.phases[1]);
  }
}
