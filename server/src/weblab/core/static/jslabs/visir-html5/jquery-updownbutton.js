
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
					var hasSentClick = false;
										
					$button.on("click", function(e) {
						//trace("click sent")
						hasSentClick = true;
						return false;
					});
						
					$button.on("mousedown touchstart", function(e) {
						//trace("mousedown: " + e.type + " " + e.target.nodeName + " " + e.target.getAttribute("class") + " " + e.target.getAttribute("src"));
						e.preventDefault();
						
						hasSentClick = false;
						
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
		
						$doc.on("mousemove.rem touchmove.rem", function(e) {							
							e = (e.originalEvent.touches) ? e.originalEvent.touches[0] : e;
							// check if the finger is still inside
			
							isTouched = _isInBounds(e, $button);
							if (isTouched) {
								_setButtonState($button, BUTTON_DOWN);
							} else {
								_setButtonState($button, BUTTON_UP);
							}
						});
						
						$doc.on("mouseup.rem", function(e) {
							//trace("mouseup.rem: " + e.type + " " + e.target.nodeName + " " + e.target.getAttribute("class") + " " + e.target.getAttribute("src"));
							_setButtonState($button, BUTTON_UP);
							$button.off(".rem");
							$doc.off(".rem");
							
							setTimeout( function() {
								if (isTouched && !hasSentClick) {
									trace("delayed click");
									$button.click();
								}
							}, 10);
							
							return false;
						});

						$doc.on("touchend.rem", function(e) {
							//trace("touchend.rem: " + e.type);
							_setButtonState($button, BUTTON_UP);
							$button.off(".rem");
							$doc.off(".rem");

								// Generate event if mouse or touch is inside the component
							if (isTouched && e.type != "mouseup") {
								$button.click();
								// guarantee that just one event will be sent, even if a browser handles both mouseup and touchend
								isTouched = false;
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