jQuery(document).ready(function() {

  callback = null;

  //Button back
  jQuery("#button_back").click(function() {
    this.blur();
    experiment.decCurrentState();
    flowState();
  });
  //Button next
  jQuery("#button_next").click(function() {
    this.blur();
    if(experiment.screens[experiment.currentState].id === 'intervencíon1' || experiment.screens[experiment.currentState].id === 'intervencíon2'){
      if(experiment.intervencion[experiment.currentPhase].length === 0){
        experiment.addCurrentState();
      }
      flowState();
    }else if(experiment.screens[experiment.currentState].id === 'enviarDatos'){
      //Llamar a función que manda los datos a firebase
      saveData();
      experiment.addCurrentState();
      flowState();
    }
    else{
      experiment.addCurrentState();
      flowState();
    }
  });
  //Botones para los ensayos
  jQuery('#yes').click(function() {
    experiment.phases[experiment.currentPhase][experiment.currentIndex].response = 1;
    this.blur();
    postResponse();
  });
  jQuery('#no').click(function() {
    experiment.phases[experiment.currentPhase][experiment.currentIndex].response = 0;
    this.blur();
    postResponse();
  });
  jQuery('#siguiente').click(function() {
    this.blur();
    jQuery('#part2').hide();
    lastTrial();
  });
  //Slider points
  jQuery("#points").bind( "change", function(event, ui) {
    experiment.juicios[experiment.currentPhase].response = jQuery(this).val();
    jQuery('footer').show();
  });
});
jQuery(document).keypress(
    function(event){
     if (event.which == '13') {
        event.preventDefault();
      }
});
function lastTrial(){
  //Incrementar indice de ensayos
  experiment.addCurrentIndex();
  if(experiment.currentIndex < experiment.phases[experiment.currentPhase].length){
    jQuery('#key').attr('src',experiment.phases[experiment.currentPhase][experiment.currentIndex].key);
    jQuery('#part1').show();
  }else{
    experiment.resetCurrentIndex();
    experiment.addCurrentState();
    flowState();
  }
}
function postResponse(){
  jQuery('#part1').hide();
  jQuery('#outcome').attr('src',experiment.phases[experiment.currentPhase][experiment.currentIndex].outcome);
  jQuery('#part2').show();
}
function inicio(cb, sex, age, course, user){
  callback = cb;

  experiment.sex = sex;
  experiment.age = age;
  experiment.course = course; //curso
  experiment.user = user; //usuario weblab

  experiment.loadPhases();
  flowState();
}
//Función para mostrar las pantallas.
function showScreen(){
  jQuery('#encabezado').text(experiment.screens[experiment.currentState].cabecera);
  jQuery('#contenido').html(experiment.screens[experiment.currentState].contenido);
  jQuery('#button_back').text(experiment.screens[experiment.currentState].btnBack);
  jQuery('#button_next').text(experiment.screens[experiment.currentState].btnNext);
  if(experiment.screens[experiment.currentState].showBtnBack === true){
    jQuery('#button_back').show();
  } else {
    jQuery('#button_back').hide();
  }
  if(experiment.screens[experiment.currentState].showBtnNext === true){
    jQuery('#button_next').show();
  } else {
    jQuery('#button_next').hide();
  }
}
//Estados por los que pasa el experimento
function flowState(){
  switch(experiment.currentState){
    case 0:
    case 1:
    case 2:
    case 3:
      showScreen();
    break;
    case 4:
      //Fase 1
      showScreen();
      prepararFase();
    break;
    case 5:
      //Juicio1
      showScreen();
      prepararJuicio();
    break;
    case 6:
      jQuery('#question').hide();
      //Intervención
      showScreen();
      var elemento = experiment.intervencion[experiment.currentPhase].shift();
      jQuery('#contenido').html(elemento.contenido);
    break;
    case 7:
      experiment.addCurrentPhase();
      //Instrucciones
      showScreen();
    break;
    case 8:
      //Fase 2
      showScreen();
      prepararFase();
    break;
    case 9:
      //Juicio2
      showScreen();
      prepararJuicio();
    break;
    case 10:
      jQuery('#question').hide();
      //Intervención 2
      showScreen();
      var elemento = experiment.intervencion[experiment.currentPhase].shift();
      jQuery('#contenido').html(elemento.contenido);
    break;
    case 11:
      //Enviar Datos
      showScreen();
    break;
    case 12:
      //Fin del experimento
      showScreen();
    break;
  }
}
function prepararFase(){
  jQuery('#key').attr('src',experiment.phases[experiment.currentPhase][experiment.currentIndex].key);
  jQuery('#questionKey').text(experiment.phases[experiment.currentPhase][experiment.currentIndex].question);
  jQuery('header,footer,hr').hide();
  jQuery('#instructions').hide();
  jQuery('#trials,#part1').show();
}
function prepararJuicio(){
  jQuery('#trials').hide();
  jQuery('#instructions,#question,header').show();
  jQuery('#contenido').html(experiment.juicios[experiment.currentPhase].question);
  jQuery("#points").val(0).slider("refresh");
}
function saveData(){
  var i,j,experimentData;
  var navegador = browserDetect();
  var fecha = new Date();
  var cadena,cadena2;
  cadena = fecha.getDate() + "/" + (fecha.getMonth()+1) + "/" + fecha.getFullYear();
  cadena2 = fecha.getHours() + ":" + fecha.getMinutes() + ":" + fecha.getSeconds();
  experimentData = experiment.code + "," + navegador + "," + cadena + "," + cadena2 + ",";
  experimentData = experimentData + experiment.subjectID + ",";
  experimentData = experimentData + experiment.age + ",";
  experimentData = experimentData + experiment.sex + ",";
  experimentData = experimentData + experiment.course + ",";
  experimentData = experimentData + experiment.group + ",";
  experimentData = experimentData + experiment.user + ",";
  experimentData = experimentData + experiment.balance + ",";
  experimentData = experimentData + experiment.juicios[0].response + ",";
  experimentData = experimentData + experiment.juicios[1].response + ",";
  for(i=0;i<experiment.phases.length;i++){
    for(j=0;j<experiment.phases[i].length;j++){
      experimentData = experimentData + experiment.phases[i][j].type + ",";
    }
  }
  for(i=0;i<experiment.phases.length;i++){
    for(j=0;j<experiment.phases[i].length;j++){
      experimentData = experimentData + experiment.phases[i][j].response + ",";
    }
  }
  var participante = {
    experimento : experiment.code,
    navegador : navegador,
    fecha : cadena,
    hora : cadena2,
    participante : experiment.subjectID,
    edad : experiment.age,
    sexo : experiment.sex,
    curso : experiment.course,
    grupo : experiment.group,
    usuario : experiment.user,
    balanceo : experiment.balance,
    juicioFase1 : experiment.juicios[0].response,
    juicioFase2 : experiment.juicios[1].response,
    tiposFase1 : [],
    tiposFase2 : [],
    respuestasFase1 : [],
    respuestasFase2 : [],
    data : experimentData
  }
  //Tipos fase 1 y respuestas fase 1
  for (i = 0;i<experiment.phases[0].length;i++) {
    participante.tiposFase1.push(experiment.phases[0][i].type);
    participante.respuestasFase1.push(experiment.phases[0][i].response);
  };
  //Tipos fase 2 y respuestas fase 2
  for (i = 0;i<experiment.phases[0].length;i++) {
    participante.tiposFase2.push(experiment.phases[1][i].type);
    participante.respuestasFase2.push(experiment.phases[1][i].response);
  };
  // Enviamos...
  console.log(participante);
  var firebase = new Firebase('https://radiant-inferno-4675.firebaseio.com/x148a');
  firebase.push(participante);
}
//Función siguiente experimento
function nextExperiment(){
  callback(100 - experiment.juicios[0].response);
}
