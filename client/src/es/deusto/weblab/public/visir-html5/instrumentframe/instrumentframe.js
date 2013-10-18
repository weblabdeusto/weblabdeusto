/* This is tightly dependent on the InstrumentRegistry, so make sure not to break the storage format */

var visir = visir || {};

visir.InstrumentFrame = function(instreg, $container)
{
	this._registry = instreg;
	this._$container = $container;

	var frame = this;

	this._showingInstrumentDialog = false;

	var protocol = window.location.protocol;
	var load_url = protocol + "//dev.openlabs.bth.se/~zeta/dav/git/loadsave/load.php";
	var save_url = protocol + "//dev.openlabs.bth.se/~zeta/dav/git/loadsave/save.php";

	var imgbase = "instrumentframe";
	if (visir.BaseLocation) imgbase = visir.BaseLocation + imgbase;
	this._baseurl = imgbase;

	//XXX: should generate a iframe name with a unique id..
	var tpl = '<div class="frame">\
	<div style="display: none">\
		<iframe name="upload_iframe" id="upload_iframe"></iframe>\
		<form action="' + load_url + '" id="upload_form" method="post" enctype="multipart/form-data" target="upload_iframe">\
			<input id="upload" name="filename" type="file" />\
		</form>\
		<form action="' + save_url + '" id="download_form" method="post" enctype="multipart/form-data" target="upload_iframe"><!-- use the upload_iframe for now-->\
			<input type="hidden" id="download_data" name="data" />\
		</form>\
	</div>\
	<div class="container">\
		<div class="instrumentdialog">\
			<div class="instrumentlist"></div>\
		</div>\
	</div>\
	<div class="buttonrow">\
		' + (!visir.Config.Get("readOnly") ?
		'<div class="loadsave">\
			<button id="loadbutton" class="">'+visir.Lang.GetMessage('load')+'</button>\
			<button id="savebutton" class="">'+visir.Lang.GetMessage('save')+'</button>\
		</div>\
		<div class="shelf"><button id="shelfbutton"><img src="%img%/images/shelf.png" /></button></div>\
		' : '') +
		'<div class="instrumentbuttons"></div>\
		<div class="measurework">\
			<button id="measurebutton" class="measure">Perform Measurement</button>\
			<div class="work_indicator"><span><img src="%img%/images/work_indicator.png" alt="work indicator"/></span></div>\
		</div>\
	</div>\
	</div>\
	';

	tpl = tpl.replace(/%img%/g, imgbase);
	var $tpl = $(tpl);

	var isTouchDevice = navigator.userAgent.match(/iPhone|iPad/);

	$container.append($tpl);

	var teacher_mode = (visir.Config) ? visir.Config.Get("teacher") : true;
	if (teacher_mode) {
		this._$container.find("div.shelf").addClass("show");
	}

	if (isTouchDevice) {
		var $dialog = $('\
		<div class="filedialog">\
			<div class="loaddialog dialog"><div class="closebutton"></div><div class="files"></div></div>\
			<div class="savedialog dialog"><div class="closebutton"></div>\
				<div>Enter file name:</div>\
				<input id="filename" type="text" />\
				<br/><button id="save">Save</button>\
				<div class="infotext">Files on portable devices are stored in the browsers local storage and will be removed if the browsers data store is cleared.</div>\
			</div>\
		</div>\
		');

		$dialog.find(".savedialog button#save").click( function() {
			var filename = $dialog.find(".savedialog input#filename").val();
			if (!filename) {
				alert("Please enter a valid filename");
				return;
			}
			frame._SaveToLocalStorage(filename);
			$dialog.find(".dialog").hide();
		});

		$dialog.find(".closebutton").click( function() {
			$dialog.find(".dialog").hide();
		});

		this._$container.find(".container").append($dialog);
	}
	instreg.AddListener( { onExperimentLoaded: function() { frame.CreateButtons(); }  })

	$container.find("#savebutton").click( function() {
		if (!isTouchDevice) {
			frame._SaveToFileSystem();
		} else {
			frame._ShowLocalStorageSaveDialog();
		}
	});

	$container.find("#loadbutton").click( function() {
		if (!isTouchDevice) {
			frame._LoadFromFileSystem();
		} else {
			frame._ShowLocalStorageLoadDialog();
		}
	});

	$container.find("#shelfbutton").click( function() {
		frame.ShowInstrumentSelection(! frame._showingInstrumentDialog);
	});

	$container.find("#upload").change( function() { $("#upload_form").submit(); })
	$container.find("#upload_iframe").unbind().load( function() {
		trace("loaded: '" + $(this).html() + "'");
		var savedata = $(this).contents().find("body").html();
		if (savedata.length == 0) return;
		instreg.LoadExperiment(savedata, $container.find(".container"));
		$container.find("#upload").val(""); // trick to make sure we get the change request even if the same file was selected
	});

	this.ShowWorkingIndicator(false);

	var me = this;

	$("body").on("working", function(e) { me.ShowWorkingIndicator(e.isWorking); });

	/// Note: the .measure button click is handled outside this class
}

visir.InstrumentFrame.prototype._SaveToFileSystem = function()
{
	var savedata = this._registry.WriteSave();
	trace(savedata);
	this._$container.find("#download_data").val(savedata);
	this._$container.find("#download_form").submit();
}

visir.InstrumentFrame.prototype._LoadFromFileSystem = function()
{
	this._$container.find("#upload").click();
}

visir.InstrumentFrame.prototype._ShowLocalStorageSaveDialog = function()
{
	this._$container.find(".dialog").hide();
	this._$container.find(".savedialog").show();
}

visir.InstrumentFrame.prototype._ShowLocalStorageLoadDialog = function()
{
	var me = this;
	var data = JSON.parse(window.localStorage.getItem("savedata")) || {};

	this._$container.find(".filedialog .loaddialog .files").empty();

	var empty = true;

	for(var key in data) {
		empty = false;

		var $file = $('<div class="file"><div class="filename">' + key + '</div><div class="delete"></div></div>');

		function genLoadFunc(loaddata) {
			return function() {
				trace("clicked load");
				me._registry.LoadExperiment(loaddata, me._$container.find(".container"));
				me._$container.find(".dialog").hide();
			}
		}

		$file.find(".filename").click(genLoadFunc(data[key]));

		function genDeleteFunc(data, filename) {
			return function() {
				var answer = confirm("Are you sure you want to delete this file?");
				if (answer) {
					// delete the file
					delete data[filename];
					window.localStorage.setItem("savedata", JSON.stringify(data));
					return me._ShowLocalStorageLoadDialog();
				}
			}
		}

		$file.find(".delete").click(genDeleteFunc(data, key));

		this._$container.find(".filedialog .loaddialog .files").append($file);
	}

	if (empty) {
		this._$container.find(".filedialog .loaddialog .files").append('<div class="infotext">No saved files</div>');
	}

	this._$container.find(".dialog").hide();
	this._$container.find(".loaddialog").show();
}

visir.InstrumentFrame.prototype._SaveToLocalStorage = function(name)
{
	if (!window.localStorage) alert("browser doesn't support local storage");
	var save = this._registry.WriteSave();
	trace("save to local storage");
	trace(save);

	var data = JSON.parse(window.localStorage.getItem("savedata")) || {};
	if (data[name]) {
		if (!confirm("Overwrite existing file?")) return;
	}
	data[name] = save;
	window.localStorage.setItem("savedata", JSON.stringify(data));
}

visir.InstrumentFrame.prototype._LoadFromLocalStorage = function(name)
{
	if (!window.localStorage) alert("browser doesn't support local storage");
	var loaddata = window.localStorage.getItem("savedata:0");
	trace("load from local storage");
	if (!loaddata) {
		alert("local storage data not found");
		return;
	}
	trace(loaddata);
	this._registry.LoadExperiment(loaddata, this._$container.find(".container"));
}

visir.InstrumentFrame.prototype.GetInstrumentContainer = function()
{
	return this._$container.find(".container");
}

visir.InstrumentFrame.prototype._CreateInstrButton = function(name)
{
	return $('<div class="buttonctnr"><button class="instrumentbutton">' + name + '</button><div class="closebutton"></div></div>');
}

visir.InstrumentFrame.prototype.CreateButtons = function()
{
	var instruments = this._registry._instruments; // watch out!

	this._$container.find(".buttonctnr").remove();
	var me = this;

	function genButtonHandler($dom) {
		return function() {
			for(var i=0;i<instruments.length; i++) {
				instruments[i].domnode.hide();
			}
			$dom.show();
			// don't continue continous measurements when we switch instruments
			$("body").trigger( { type:"working", isWorking: false, shouldContinue: false });
		}
	}

	function genCloseButtonHandler($btnctnr, instr) {
		return function() {
			me._registry.RemoveInstrument(instr);
			$btnctnr.remove(); // remove this button
			me.ShowFirstInstrument();
			$("body").trigger("configChanged"); // notify so we can update instrument connections
		}
	}

	for(var i=0;i<instruments.length; i++) {
		var instr = instruments[i];
		var suffix = "";
		if (instruments[i].id > 1) suffix += " " + instruments[i].id;
		var $newButton = this._CreateInstrButton( instr.instrInfo.displayname + suffix);
		$newButton.find(".instrumentbutton").click( genButtonHandler(instr.domnode));
		$newButton.find(".closebutton").click( genCloseButtonHandler($newButton, instruments[i]));
		this._$container.find(".instrumentbuttons").append($newButton);
	}

	this.ShowFirstInstrument();
}

visir.InstrumentFrame.prototype.ShowFirstInstrument = function()
{
	this._$container.find(".container > .instrument").hide();
	this._$container.find(".container > .instrument").first().show();
}

visir.InstrumentFrame.prototype.ShowWorkingIndicator = function(show)
{
	this._$container.find(".work_indicator img").toggle(show);
}

visir.InstrumentFrame.prototype._PopulateInstrumentDialog = function()
{
	var url = this._baseurl + "/instruments.xml";

	var $list = this._$container.find(".instrumentlist");
	$list.empty();

	var me = this;

	$.get(url, function(rawxml) {
		var $xml = $(rawxml);
		trace("instrument library loaded");
		$xml.find("instruments > instrument").each( function(e) {
			var $elem = $(this);
			var id = $elem.attr("id");
			var displayname = visir.Lang.GetDescription($elem.attr("displayname"));
			var type = $elem.attr("type");
			var image = $elem.attr("image");
			var path = $elem.attr("path"); // this is the swf path, do not use
			var jsclass = $elem.attr("jsclass");

			var elem = '<div class="list-elem"><img src="%img%/' + image + '" /><div class="title">' + displayname + '</div></div>';
			elem = elem.replace(/%img%/g, me._baseurl);
			var $elem = $(elem);
			$elem.click(function(e) {
				trace("moot!");
				if (me._registry._instruments.length >= 6) return;
				me._registry.CreateInstrFromJSClass(jsclass, me._$container.find(".container"));
				me.CreateButtons();
				me._$container.find(".instrumentbuttons .closebutton").show();
				$("body").trigger("configChanged"); // notify so we can update instrument connections
			});

			$list.append($elem);
		});
	});
}

visir.InstrumentFrame.prototype.ShowInstrumentSelection = function(show)
{
	this._showingInstrumentDialog = show;
	if (show) {
		this._PopulateInstrumentDialog();
		//this._$container.find("div.shelf").toggleClass("show");
		this._$container.find(".instrumentdialog").show();
		this._$container.find(".instrumentbuttons .closebutton").show();
	} else {
		this._$container.find(".instrumentdialog").hide();
		this._$container.find(".instrumentbuttons .closebutton").hide();
	}
}

visir.InstrumentFrame.prototype.ShowDeleteButtons = function(show)
{
	this._$container.find(".instrumentbuttons .closebutton").toggleClass("show");
}