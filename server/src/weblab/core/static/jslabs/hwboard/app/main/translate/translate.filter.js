
angular
    .module("hwboard")
    .filter("translate", translateFilter);


/**
 * Filter to handle translations.
 * It will search for the trimmed string, but it will respect the trim nonetheless.
 * That is, " ORIGINAL " will be translated by looking up "ORIGINAL" but " TRANSLATION "
 * will be returned.
 * @returns {translate}
 */
function translateFilter() {
    return translate;

    function translate(text) {
        var trimmed = text.trim();
        
        var ret = TRANSLATIONS[trimmed];
        if (ret != undefined)
            // Keep the trim that we removed for the lookup.
            return text.replace(trimmed, ret);
        else
            return text;
    }
}