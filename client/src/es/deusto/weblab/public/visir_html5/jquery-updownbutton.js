
(function( $ ){
	
	function _isInBounds(touch, $elem) {
		var offset = $elem.offset(),
		width = $elem.outerWidth(),
		height = $elem.outerHeight(),
		left = offset.left,
		right = left + width,
		top = offset.top,
		bottom = top + height,
		touchX = touch.pageX,
		touchY = touch.pageY;

		return (touchX > left && touchX < right && touchY > top && touchY < bottom);
	}

	var BUTTON_DOWN = true;
	var BUTTON_UP = false;
	function _setButtonState($button, down) {
		if (down) {
			$button.find("img.up").removeClass("active");
			$button.find("img.down").addClass("active");		
		} else {
			$button.find("img.down").removeClass("active");
			$button.find("img.up").addClass("active");
		}
	}
	
	var methods = {
		init : function( props ) {
			var options = $.extend({
				}, props || {});
			
			return this.each(function() {
					var $doc = $(document);
					var $button = $(this);
					var isTouched = false;
	
					$button.on("mousedown touchstart", function(e) {
						e.preventDefault();
						_setButtonState($button, BUTTON_DOWN);
		
						isTouched = true;
		
						$button.on("mouseover.rem", function(e) {
							_setButtonState($button, BUTTON_DOWN);
							isTouched = true;
						});

						$button.on("mouseout.rem touchleave.rem", function(e) {
							_setButtonState($button, BUTTON_UP);
							isTouched = false;
						});
		
						$doc.on("touchmove.rem", function(e) {
							e = (e.originalEvent.touches) ? e.originalEvent.touches[0] : e;
							// check if the finger is still inside
			
							isTouched = _isInBounds(e, $button);
							if (isTouched) {
								_setButtonState($button, BUTTON_DOWN);
							} else {
								_setButtonState($button, BUTTON_UP);
							}
						});
		
						$doc.on("mouseup.rem touchend.rem", function(e) {
							_setButtonState($button, BUTTON_UP);
		
							$button.off(".rem");
							$doc.off(".rem");
			
							if (isTouched) {
								$button.click();
							}
						});
					});

			});
		},
		destroy : function( ) {
			return this.each(function(){
			});
		}

	};

	$.fn.updownButton = function( method ) {

		if ( methods[method] ) {
			return methods[method].apply( this, Array.prototype.slice.call( arguments, 1 ));
		} else if ( typeof method === 'object' || ! method ) {
			return methods.init.apply( this, arguments );
		} else {
			$.error( 'Method ' +  method + ' does not exist on jQuery.updownButton' );
		}    

	};

})( jQuery );