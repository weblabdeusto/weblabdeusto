{
	// IMPORTANT
	//
	// Internet Explorer can't parse dictionaries as:
	//  {
	//        'foo' : 'bar',
	//  }
	//
	// Due to the last ',' after 'bar'. Same for lists
	//   [
	//      1,
	//      2,
	//      //3
	//   ]
	// Would produce an error since there is a ',' and then a ']'.
	//
	// "weblab.service.fileupload.post.url" : "/weblab/fileUpload.php",
	"development"                    : true, // To see the latest features, although they might not be working
	"demo.available"                 : true,
	"sound.enabled"					 : false,
	"admin.email"                    : "weblab@deusto.es",
	"google.analytics.tracking.code" : "UA-12576838-6",
	"experiments.default_picture"	 : "/img/experiments/default.jpg",
	"host.entity.image.login"        : "/img/udeusto-logo.jpg",
	"host.entity.image"              : "/img/udeusto-logo-main.jpg",
	"host.entity.image.mobile"       : "/img/udeusto-logo-mobile.jpg",
	"host.entity.link"               : "http://www.deusto.es/",
    "facebook.like.box.visible"      : false
}