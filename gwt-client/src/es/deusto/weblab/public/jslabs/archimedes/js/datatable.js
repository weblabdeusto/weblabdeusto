

// the semi-colon before function invocation is a safety net against concatenated
// scripts and/or other plugins which may not be closed properly.
;(function ( $, window, document, undefined ) {

		// undefined is used here as the undefined global variable in ECMAScript 3 is
		// mutable (ie. it can be changed by someone else). undefined isn't really being
		// passed in so we can ensure the value of it is truly undefined. In ES5, undefined
		// can no longer be modified.

		// window and document are passed through as local variable rather than global
		// as this (slightly) quickens the resolution process and can be more efficiently
		// minified (especially when both are regularly referenced in your plugin).

		// Create the defaults once
		var pluginName = "datatable",
				defaults = {
                    // Header text
			        header: "Sensors",

                    // Variables and values. May be functions.
                    vars: {
                        "Liquid Level" : "17 cm.",
                        "Ball Weight" : function() { return "25 gr."; }
                    },

                    // Translator function. If not null, it will be used to
                    // translate every text.
                    translator : null
		};

		// The actual plugin constructor
		function Plugin ( element, options ) {
            this.element = element;
            // jQuery has an extend method which merges the contents of two or
            // more objects, storing the result in the first object. The first object
            // is generally empty as we don't want to alter the default options for
            // future instances of the plugin
            this.settings = $.extend( {}, defaults, options );
            this._defaults = defaults;
            this._name = pluginName;


            // To store the elements that correspond to the variables,
            // identified by their header name or functor.
            // Items are contained within as a [elem, tr] list.
            this._varElements = {};

            this._table = {};

            this.init();
		}

		Plugin.prototype = {
            init: function () {
                // Place initialization logic here
                // You already have access to the DOM element and
                // the options via the instance, e.g. this.element
                // and this.settings
                // you can add more functions like the one below and
                // call them like so: this.yourOtherFunction(this.element, this.settings).
                //console.log("[DataTable]: Initializing table.");
                return this._createTable();
            },

            // Creates the table for the first time.
            _createTable: function() {
                var table = $("<table>").appendTo($(this.element));
                this._table = table;
                table.attr("class", "table table-bordered table-condensed");

                var thead = $("<thead>").appendTo(table);
                var header_tr = $("<tr>").appendTo(thead);
                var th = $("<th>").appendTo(header_tr);
                $("<th>").appendTo(header_tr);
                th.text(this.getText(this.settings.header));

                var tbody = $("<tbody>").appendTo(table);

                var that = this;
                $.each(this.settings.vars, function(key, value) {
                    var tr = $("<tr>").appendTo(tbody);
                    var td_key = $("<td>").appendTo(tr);
                    var td_value = $("<td>").appendTo(tr);

                    that._varElements[key] = [td_value, tr];

                    td_key.text(that.getText(key));
                    td_value.text(value);
                });

                return table;
            },


            //! Updates the text in a specified variable.
            //!
            //! @param variable: Header to identify the variable.
            update: function(variable) {
                var v = this._varElements[variable][0];
                var newText = this.getText(this.settings.vars[variable]);
                var oldText = v.text();

                if(newText !== oldText)
                {
                    // Update the text.
                    v.text(newText);

                    // Add feedback on the updated text.
                    this._varElements[variable][1]
                        .css("-webkit-transition","all 0.6s ease")
                        .css("backgroundColor","white")
                        .css("-moz-transition","all 0.6s ease")
                        .css("-o-transition","all 0.6s ease")
                        .css("-ms-transition","all 0.6s ease")

                        .css("backgroundColor", "rgba(200, 255, 200, 1)").delay(800).queue(function() {
                            $(this).css("backgroundColor","white");
                            $(this).dequeue(); //Prevents box from holding color with no fadeOut on second click.
                        });
                }
            },

            //! Full update.
            updateAll: function() {
                var that = this;
                $.each(this._varElements, function(ident, element) {
                    that.update(ident);
                });
            },


            // Checks if the specified variable is hidden.
            getElement : function(variable) {
                return this._varElements[variable][0];
            },

            //! Hides the specified variable.
            hide : function(variable) {
                this._varElements[variable][1].hide();
            },

            //! Shows the specified variable.
            show : function(variable) {
                this._varElements[variable][1].show();
            },

            //! Hides everything.
            hideAll : function() {
                this._table.hide();
            },

            showAll : function() {
                this._table.show();
            },

            //! Gets the actual text that corresponds to the specified text,
            //! depending on whether it is a function, on the translation
            //! settings, etc.
            getText: function(text) {
                // Gets the actual text to display depending on the settings.
                if($.isFunction(text)) {
                    // If it is a function call it to obtain the actual value.
                    return text();
                } else {
                    if($.isFunction(this.settings.translator)) {
                        // If we are configured to use a translator, use the text it returns.
                        return this.settings.translator(text);
                    } else {
                        // Otherwise just use the text itself.
                        return text;
                    }
                }
            }, // !getText

            test : function(txt) {
                console.log(this);
                console.log(txt);
            }

		};

		// A really lightweight plugin wrapper around the constructor,
		// preventing against multiple instantiations
		$.fn[ pluginName ] = function ( optionsOrMethod ) {

            var args = arguments;
            var ret;

            this.each(function() {
                var data = $.data(this, "plugin_" + pluginName);
                if ( !data ) {
                        $.data( this, "plugin_" + pluginName, new Plugin( this, optionsOrMethod ) );
                } else {
                    if( data[optionsOrMethod] ) {
                        ret = data[optionsOrMethod].apply(data, Array.prototype.slice.call(args, 1));
                        return false;
                    } else {
                        ret = data;
                    }
                }
            });

            // TODO: Improve this.
            if(this.length == 1)
                return ret;
            else
                return this;
		};

})( jQuery, window, document );