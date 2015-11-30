angular
    .module("hwboard")
    .directive("wlTranslateMe", wlTranslateMe);

/**
 * Attribute directive to handle translation of the text within a tag.
 * The element to be translated can contain child items. The child items
 * will be kept as-is, only the text nodes will be replaced. This is useful,
 * for instance, to be able to embed icon tags.
 */
function wlTranslateMe($filter) {
    return {
        restrict: "A",
        transclude: false,
        link: function(scope, element, attrs) {
            var originalText = element.text();
            var newText = $filter("translate")(originalText);

            // This is easier but it is commented out because it removes child elements while setting the new text.
            // This is inconvenient for icons.
            // element.text(newText);

            // Replace *only* the text elements with the translation.
            element.contents().filter(function(){ return this.nodeType == 3; }).replaceWith(newText);
        }
    }
}