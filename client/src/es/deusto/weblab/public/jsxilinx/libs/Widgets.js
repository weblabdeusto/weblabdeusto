//! This script contains several stand-alone widgets (not directly
//! dependant on Weblab) and some general-purpose utility functions,
//! which can probably be used for several different JSXILINX-based
//! experiments.



_page_dim = false;

function dim_page() {

    if (_page_dim != undefined && _page_dim == true)
        return;

    var dimmingElement = document.createElement('div');
    dimmingElement.id = "dim";
    dimmingElement.className = "dim";
    document.body.appendChild(dimmingElement);

    _page_dim = true;
}

function light_page() {
    var dimmingElement = document.getElementById('dim');
    document.body.removeChild(dimmingElement);
    _page_dim = false;
}


//! The following code is used to refresh the webcam 
//! It is refreshed frame-by-frame every second.
RefreshingCameraWidget = function (targetid, imgsrc) {

    var mTick = 0;
    var mImage = new Image();
    var mReload = (new Date()).getTime();

    var mTargetId;
    var mImgSrc;

    var mRestart = 0;

    this._init = function () {
        mTargetId = targetid;
        mImgSrc = imgsrc;
    }

    mImage = mImgSrc + "?" + mReload;

    this.startRefreshing = function () {
        mTick++;
        if (mTick > 3) { mRestart = 1; } else { mRestart = 0; }
        if (mImage.complete) {
            mTick = 0;
            //console.log("Changing: " + mImage.src);
            //console.log(document[mTargetId]);
            document.images[mTargetId].src = mImage.src;
            mImage = new Image();
            mReload = (new Date()).getTime();
            mImage.src = mImgSrc + "?" + mReload;

        }
        if (mRestart) {
            mTick = 0;
            mImage = new Image();
            mReload = (new Date()).getTime();
            mImage.src = mImgSrc + "?" + mReload;
        }

        setTimeout(this.startRefreshing.bind(this), 3000);
    }


    this._init();
};








//! Base Image widget
//!
//! @param pos_x X position of the image (left top corner). 
//! As a CSS string or a pixel-integer.
//! @param pos_y Y position of the image (left top corner). 
//! As a CSS string or a pixel-integer.
//! @param text Text beneath the image
//! @param imgwidth CSS string describing the image width
//! @param imgheight CSS string describing the image height
//! @param imgsrc Src URL for the image
ImageWidget = function (pos_x, pos_y, text, imgwidth, imgheight, imgsrc) {

    var mWidImg;
    var mWidContainer;
    var mTextSpan;
    var mOnClickCB;

    this._init = function () {
        this._createElement(pos_x, pos_y, text, imgwidth, imgheight, imgsrc);
    }

    this._getTextSpan = function () {
        return mTextSpan;
    }

    this._getImageElement = function () {
        return mWidImg;
    }

    this._getContainerElement = function () {
        return mWidContainer;
    }

    this._getOnClickCB = function () {
        return mOnClickCB;
    }

    this._createElement = function (pos_x, pos_y, text, imgwidth, imgheight, imgsrc) {
        mWidImg = document.createElement('img');
        if (imgwidth != undefined)
            mWidImg.style.width = imgwidth;
        if (imgheight != undefined)
            mWidImg.style.height = imgheight;
        mWidImg.onclick = this.onClick.bind(this);

        if (imgsrc != undefined)
            mWidImg.src = imgsrc;

        mTextSpan = document.createElement('span');
        mTextSpan.style.color = "white";
        mTextSpan.style.fontWeight = "bold";
        mTextSpan.style.fontSize = "large";
        mTextSpan.style.textAlign = "center";
        mTextSpan.innerHTML = "<br>" + text;

        mWidContainer = document.createElement('div');
        mWidContainer.style.position = 'absolute';
        mWidContainer.style.textAlign = "center";

        if (typeof pos_x == "number")
            mWidContainer.style.left = "" + pos_x + "px";
        else
            mWidContainer.style.left = pos_x;

        if (typeof pos_y == "number")
            mWidContainer.style.top = "" + pos_y + "px";
        else
            mWidContainer.style.top = pos_y;

        mWidContainer.appendChild(mWidImg);
        mWidContainer.appendChild(mTextSpan);

        return mWidContainer;
    }

    this.changeImage = function (imgsrc) {
        if(imgsrc != mWidImg.src)
            mWidImg.src = imgsrc;
    }

    this.setText = function (text) {
        mTextSpan.innerHTML = "<br>" + text;
    }

    this.onClick = function () {
        if (mOnClickCB != undefined)
            mOnClickCB();
    }

    this.setOnClick = function (func) {
        mOnClickCB = func;
    }

    this.getElement = function () {
        return mWidContainer;
    }

    this._init();
};




//! To easily control the progress bar. It depends
//! on a previously placed progress bar, and on 
//! CSS styles on the page.
//!
ProgressBarWidget = function (posx, posy) {

    var mProgressBar = $("#progressbar");
    var mProgressLabel = $(".progress-label");

    this._init = function () {
        mProgressBar.position = "absolute";
        mProgressBar.css("left", posx);
        mProgressBar.css("top", posy);

        mProgressBar.progressbar({
            value: false,
            change: function () { },
            complete: function () { }
        });
    }

    this.hide = function () {
        mProgressBar.hide();
        light_page();
    }

    this.show = function () {
        dim_page();
        mProgressBar.show();
    }

    //! Note: It is not clear whether the JQUERY-UI method that this depends on
    //! behaves as intended or not.
    //!
    //! Either way, it seems that it works the following way:
    //!
    //! If it is determined to "false", then the progress bar is indeterminate.
    //! That is, a continuous but not finite progress animation appears.
    //!
    //! However, if the determination is set to a specific value, currently configured
    //! to be between 0 and 100, then the progress bar does not have an animation, but
    //! a background progress indication set to the specified value.
    //!
    //! Common use cases hence are:
    //! - Setting determined to false and a text, to indicate that the page is working on something,
    //! but that the progress of that activity is not known.
    //! - Setting determined to a specific integer value, to indicate the actual, known, percentual progress.
    //! - Setting determined to 100 and a text, to use the progress bar a status box, indicating that no progress is
    //! being made but showing text in the bar nonetheless.
    this.setDetermination = function (determined) {
        mProgressBar.progressbar("value", determined);
    }

    this.setText = function (text) {
        mProgressLabel.text(text);
    }

    this._init();
}




//! FullScreen Widget. Switches between windowed mode and full screen.
//!
FullScreenWidget = function (pos_x, pos_y, text) {

    var mFullScreenImg = "http://cdn1.iconfinder.com/data/icons/bloggers-1-to-7-vol-PNG/512/full_screen.png";

    ImageWidget.call(this, pos_x, pos_y, text, "50px", "50px", mFullScreenImg);

    this._init = function () {
        this.setOnClick(this.onClick.bind(this));
        this.getElement().style.zIndex = 2;
    }


    this.onClick = function () {

        console.log("Fullscreen request received");

        if (THREEx.FullScreen.available() == false) {
            console.error("FullScreen is not available in your system");
            this.setText("[Unavailable]");
        }

        if (THREEx.FullScreen.activated() == false) {
            THREEx.FullScreen.request();
        }
        else
            THREEx.FullScreen.cancel();
    }


    this._init();

};



//! LED Widget. Simply used to display the state of the LEDs. 
//! Which can either be on or off.
//!
//! @param pos_x X position of the image (left top corner). 
//! As a CSS string or a pixel-integer.
//! @param pos_y Y position of the image (left top corner). 
//! As a CSS string or a pixel-integer.
//! @param text Text beneath the image
LEDWidget = function (pos_x, pos_y, text) {

    var mState;

    var mOffImg = "../../img/led_gray.png";
    var mOnImg = "../../img/led_red.png";

    ImageWidget.call(this, pos_x, pos_y, text, "50px", "50px");

    this._init = function () {
        this.setState(false);
    }

    this.setState = function setState(state) {
        mState = state;
        if (state)
            this.changeImage(mOnImg);
        else
            this.changeImage(mOffImg);
    }

    this.getState = function getState() {
        return mState;
    }

    this._init();
};