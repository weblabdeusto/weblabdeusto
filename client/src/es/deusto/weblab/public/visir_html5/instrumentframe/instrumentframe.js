/* This is tightly dependent on the InstrumentRegistry, so make sure not to break the storage format */

var visir = visir || {};

visir.InstrumentFrame = function(instreg, $container)
{
	this._registry = instreg;
	this._$container = $container;

	var protocol = window.location.protocol;
	var load_url = protocol + "//dev.openlabs.bth.se/~zeta/dav/git/loadsave/load.php";
	var save_url = protocol + "//dev.openlabs.bth.se/~zeta/dav/git/loadsave/save.php";

	//XXX: should generate a iframe name with a unique id..
	var $tpl = $(
	'<div class="frame">\
	<div style="display: none">\
		<iframe name="upload_iframe" id="upload_iframe"></iframe>\
		<form action="' + load_url + '" id="upload_form" method="post" enctype="multipart/form-data" target="upload_iframe">\
			<input id="upload" name="filename" type="file" />\
		</form>\
		<form action="' + save_url + '" id="download_form" method="post" enctype="multipart/form-data" target="upload_iframe"><!-- use the upload_iframe for now-->\
			<input type="hidden" id="download_data" name="data" />\
		</form>\
	</div>\
	<div class="container"></div>\
	<div class="buttonrow">\
		<div class="loadsave"></div>\
		<div class="instrumentbuttons"></div>\
		<button id="measurebutton" class="measure">Perform Measurement</button>\
	</div>\
	</div>\
	'
	);

	var isTouchDevice = navigator.userAgent.match(/iPhone|iPad/);
	if (!isTouchDevice) {
		$loadsave = $(
			'<button id="loadbutton" class="">Load</button>\
			<button id="savebutton" class="">Save</button>\
			');
			$tpl.find(".loadsave").append($loadsave);
	}

	$container.append($tpl);

	var frame = this;
	instreg.AddListener( { onExperimentLoaded: function() { frame.CreateButtons(); }  })

	$container.find("#savebutton").click( function() {
		trace(instreg.WriteSave());
		$container.find("#download_data").val(instreg.WriteSave());
		$container.find("#download_form").submit();
	});

	$container.find("#loadbutton").click( function() {
		$container.find("#upload").click();
	});

	$container.find("#upload").change( function() { $("#upload_form").submit(); })
	$container.find("#upload_iframe").unbind().load( function() {
		trace("loaded: '" + $(this).html() + "'");
		var savedata = $(this).contents().find("body").html();
		if (savedata.length == 0) return;
		instreg.LoadExperiment(savedata, $container.find(".container"));
		$container.find("#upload").val(""); // trick to make sure we get the change request even if the same file was selected
	});

	/// Note: the .measure button click is handled outside this class
}

visir.InstrumentFrame.prototype.GetInstrumentContainer = function()
{
	return this._$container.find(".container");
}

visir.InstrumentFrame.prototype._CreateInstrButton = function(name)
{
	return $('<button class="instrumentbutton">' + name + '</button>');
}

visir.InstrumentFrame.prototype.CreateButtons = function()
{
	var instruments = this._registry._instruments; // watch out!

	this._$container.find(".instrumentbutton").remove();
	var me = this;

	function genButtonHandler($dom) {
		return function() {
			for(var i=0;i<instruments.length; i++) {
				instruments[i].domnode.hide();
			}
			$dom.show();
		}
	}

	for(var i=0;i<instruments.length; i++) {
		var instr = instruments[i];
		var suffix = "";
		if (instruments[i].id > 1) suffix += " " + instruments[i].id;
		var $newButton = this._CreateInstrButton( instr.instrInfo.displayname + suffix);
		$newButton.click( genButtonHandler(instr.domnode));
		this._$container.find(".instrumentbuttons").append($newButton);
	}

	this._$container.find(".container > .instrument").hide();
	this._$container.find(".container > .instrument").first().show();
}