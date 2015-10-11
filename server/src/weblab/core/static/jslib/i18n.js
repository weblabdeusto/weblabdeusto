function getMessage(key) {
    var languageMessages = MESSAGES[weblab.locale]
    if (languageMessages === undefined || languageMessages[key] === undefined) {
        message = MESSAGES["en"][key];
        if (message === undefined) {
            message = "Message '" + key + "' not found";
        } 
    } else {
        message = languageMessages[key];
    }
    return message;
};
