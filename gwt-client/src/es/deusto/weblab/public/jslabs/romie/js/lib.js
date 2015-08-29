function fisherYates (myArray) {
  var i = myArray.length, j, tempi, tempj;
  if ( i === 0 ) return false;
  while ( --i ) {
     j = Math.floor( Math.random() * ( i + 1 ) );
     tempi = myArray[i];
     tempj = myArray[j];
     myArray[i] = tempj;
     myArray[j] = tempi;
   }
}
/*Función que inserta el copyright en un párrafo*/
function insertCopyright() {
    var copy = '&copy;' + insertDevelopers() + experiment.year + '. Estás ' +
    'autorizado a utilizar este programa con fines de investigación ' +
    'o docencia, con o sin modificaciones, con la única condición de ' +
    'que cites a los autores, el nombre del programa y la página web ' +
    'donde puede descargarse. Se prohibe expresamente la publicación ' +
    'de este programa en otros sitios o medios, así como cualquier ' +
    'utilización comercial del mismo sin el permiso explícito de los ' +
    'autores.';
  return copy;
}
/*Función que inserta los desarrolladores en un párrafo*/
function insertDevelopers() {
  var longitud = experiment.developers.length;
  var cadena = "";
  if(longitud === 1) {
    cadena = experiment.developers[0] + " ";
  } else {
    for(var i=0;i<longitud;i++) {
      if(i < longitud-2) {
        cadena = cadena + experiment.developers[i] + ", ";
      } else if(i < longitud-1) {
        cadena = cadena + experiment.developers[i];
      } else {
        if(experiment.language === "es")
        {
          cadena = cadena + " y " + experiment.developers[i] + " ";
        }
        else if(experiment.language === "en")
        {
          cadena = cadena + " and " + experiment.developers[i] + " ";
        }
      }
    }
  }
  return cadena;
}
//Función que muestra y oculta las referencias
function hideAndShowReferences() {
  elemento = document.getElementById('references');
  if(elemento.style.visibility === 'visible') {
    hideVisibility(['references']);
  } else {
    var texto = 'Software de psicología experimental.<br>' +
      'Versión 1.0, Español, ' + experiment.year + '.<br>' +
      'http://www.labpsico.com' + insertCopyright();
    injectText(['references'],[texto]);
    showVisibility(['references']);
  }
  jQuery('a').blur();
}
//Función que valida el formulario de datos del participante
function validate() {
  experiment.sex = jQuery( "#sexo" ).val();
  var age = parseInt(jQuery('#edad').val());
  var curso = jQuery('#curso').val();
  var usuario = jQuery('#user').val();
  if(age === "" || isNaN(age) || curso === "" || usuario === ""){
    alert('Rellene todos los campos');
  } else{
    experiment.age = age;
    experiment.course = curso;
    experiment.user = usuario
    experiment.addCurrentState();
    flowState();
  }
}
/**************************************************************************
***************************************************************************
************************Experiment Functions*******************************
***************************************************************************
**************************************************************************/
/*Information about style.visibility and style.display*/
/*Hiding an element can be done by setting the display property to "none" or
the visibility property to "hidden". However, notice that these two methods
produce different results:
visibility:hidden hides an element, but it will still take up the same space
as before. The element will be hidden, but still affect the layout.
display:none hides an element, and it will not take up any space. The element
will be hidden, and the page will be displayed as if the element is not there*/
/*Hide and show elements*/
function hideVisibility(elementsList) {
  for (var i=0;i<elementsList.length;i++) {
    document.getElementById(elementsList[i]).style.visibility = "hidden";
  }
}
function showVisibility(elementsList) {
  for (var i=0;i<elementsList.length;i++) {
    document.getElementById(elementsList[i]).style.visibility = "visible";
  }
}
/*Hide and show messages*/
function hideDisplay(elementsList) {
  for (var i=0;i<elementsList.length;i++) {
    document.getElementById(elementsList[i]).style.display = "none";
  }
}
function showDisplay(elementsList) {
  for (var i=0;i<elementsList.length;i++) {
    document.getElementById(elementsList[i]).style.display = "block";
  }
}
/*Insert text*/
function injectText(idList,textList) {
  for (var i=0;i<idList.length;i++) {
    document.getElementById(idList[i]).innerHTML = textList[i];
  }
}
/*Insert images*/
function insertImages(idList,sourceList) {
  for (var i=0;i<idList.length;i++) {
    document.getElementById(idList[i]).source = sourceList[i];
  }
}
/*Focus remove*/
function removeFocus(idList) {
  for(var i=0;i<idList.length;i++) {
    document.getElementById(idList[i]).blur();
  }
}
/*activar desactivar botones*/
function enabledButtons(idList)
{
  for(var i=0;i<idList.length;i++) {
    var button = document.getElementById(idList[i]);
    button.disabled = false;
  }
}
function disabledButtons(idList)
{
  for(var i=0;i<idList.length;i++) {
    var button = document.getElementById(idList[i]);
    button.disabled = true;
  }
}
/*Funcion que crea y retorna un array con una secuencia aleatoria,
 "total" es el número de elementos del array.
 "number_outcomes" es el número de elementos con outcomes del array.
 "number_no_outcomes" es el número de elementos con no outcomes del array.
 */
function generateSequence(total,number_outcomes,number_no_outcomes)
{
  var sequence = new Array(total);
  for(var i=0;i<total;i++)
  {
    if(i < number_outcomes)
      sequence[i] = 1;
    else
      sequence[i] = 0;
  }
  fisherYates(sequence);
  return (sequence);
}
function sendOnlineData(data)
{
  var storageItem = data;
  xhr = new XMLHttpRequest();
  xhr.open('POST', "datasent.asp", true);
  xhr.setRequestHeader("Content-type","application/x-www-form-urlencoded");
  xhr.onreadystatechange = function (e) { 
    if (xhr.readyState === 4) {
       if (xhr.status === 200) {
         window.console.log('Sent!');
       } else {
         window.console.log('Error ' + xhr.status);
       }
    }
  };   
  xhr.send('data=' + data);
  if (Modernizr.localstorage) {
    window.localStorage.setItem(storageItem, data);
  }
}
/*****************************************
**** Write data to file
*****************************************/
function browserDetect()
{
  if(navigator.userAgent.toLowerCase().indexOf('chrome') !=-1)
  {
    return 'Chrome';
  }
  if (navigator.userAgent.indexOf('MSIE') !=-1) 
  {
        return 'Internet Explorer';
  }
  if (navigator.userAgent.indexOf('Firefox') !=-1) 
  {
        return 'Firefox';
  }
  if (navigator.userAgent.indexOf('Safari') !=-1)
  {
    return 'Safari';
  }
  if (navigator.userAgent.indexOf('Opera') !=-1)
  {
    return 'Opera';
  }
  else
  {
    var rv = getInternetExplorerVersion();
    if(rv === -1){
      return 'Navegador desconocido';
    }else {
      return 'Internet explorer' + String(rv);
    }
  }
}
function getInternetExplorerVersion()
{
  var rv = -1;
  if (navigator.appName == 'Microsoft Internet Explorer')
  {
    var ua = navigator.userAgent;
    var re  = new RegExp("MSIE ([0-9]{1,}[\.0-9]{0,})");
    if (re.exec(ua) != null)
      rv = parseFloat( RegExp.$1 );
  }
  else if (navigator.appName == 'Netscape')
  {
    var ua = navigator.userAgent;
    var re  = new RegExp("Trident/.*rv:([0-9]{1,}[\.0-9]{0,})");
    if (re.exec(ua) != null)
      rv = parseFloat( RegExp.$1 );
  }
  return rv;
}