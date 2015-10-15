(function( $ ){
	var methods = {
		init : function( props ) {
			var options = $.extend({
				offset: 0,
				move: function(elem, x, y, newtouch){ }
				}, props || {});
			
			return this.each(function(){

				var doc = $(document);
				var handle = $(this);
				//var top = handle.find(".top");
				
				var newTouch = true;

				handle.on("mousedown touchstart", function(e) {

					e.preventDefault();
					
					// try to avoid having to calculate the size and offset of the turnable each move event
					var offset = handle.offset();
					/*var center = { x: top.width() / 2, y: top.height() / 2 };
					var origin = top.css("transform-origin");
					if (origin) {
						var sp = origin.split(" ");
						center.x = parseInt(sp[0]);
						center.y = parseInt(sp[1]);
					}	*/				

					doc.on("mousemove.rem touchmove.rem", function(e) {

						e = (e.originalEvent.touches) ? e.originalEvent.touches[0] : e;
						
						var offset = handle.parent().offset();

						var dx = e.pageX - offset.left;
						var dy = e.pageY - offset.top;
						
						//trace("dx/dy: " + dx + " " + dy);
						
						var p = options.move(handle, dx, dy, newTouch);
						//trace("p: " + p.x + " " + p.y);
						if (p.x != undefined) handle.css("left", p.x + "px");
						if (p.y != undefined) handle.css("top", p.y + "px");

						/*var deg = Math.atan2(dy, dx) * 180 / Math.PI;
						deg = (deg + 360) % 360;
						var userdeg = options.turn(handle, deg, newTouch);
						if (userdeg != undefined) {
							setRotation(top, userdeg + options.offset); // XXX: not portable..
						}*/
						
						newTouch = false;
					});

					doc.on("mouseup.rem touchend.rem", function(e) {
						handle.off(".rem");
						doc.off(".rem");
						newTouch = true;
					});
				});

			});
		},
		destroy : function( ) {
			return this.each(function(){
			});
		}


	};

	$.fn.draggable = function( method ) {

		if ( methods[method] ) {
			return methods[method].apply( this, Array.prototype.slice.call( arguments, 1 ));
		} else if ( typeof method === 'object' || ! method ) {
			return methods.init.apply( this, arguments );
		} else {
			$.error( 'Method ' +  method + ' does not exist on jQuery.draggable' );
		}    

	};

})( jQuery );