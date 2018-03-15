/*
Copyright 2018 Brian J. Duerst

This drives the front end for the 'cat or not a cat' application.
Meant to be used with a Google Cloud Compute course.
 */

// Link the instant/deferred checkbox to the form's checkbox
var checkboxVisible = document.querySelector('#switch-1');
var checkboxInvisible = document.querySelector('#switch-2');
var setting = getCookie("setting");
if (setting === "true") {
    checkboxVisible.checked = true;
    checkboxInvisible.checked = true;
} else if (setting === "false") {
    checkboxVisible.checked = false;
    checkboxInvisible.checked = false;
}
else {
    setCookie("setting", false, 365);
}
checkboxVisible.addEventListener('click', function () {
    checkboxInvisible.checked = checkboxVisible.checked;
    cookieStorage = checkboxVisible.checked;
    setCookie("setting", checkboxVisible.checked, 365);
});

// Upload Image File - Dialogue Controls
var dialog = document.querySelector('#image-dialog');
var showDialognav = document.querySelector('#show-dialog-nav');
var showDialogButton = document.querySelector('#show-dialog');
if (!dialog.showModal) {
    dialogPolyfill.registerDialog(dialog);
}

// Open the image dialog
showDialognav.addEventListener('click', function () {
    dialog.showModal();
});
showDialogButton.addEventListener('click', function () {
    dialog.showModal();
});

// Close the image dialog
dialog.querySelector('#close-image-dialog').addEventListener('click', function () {
    dialog.close();
    document.getElementById("uploadFile").value = null;
    document.getElementById('submit-button').MaterialButton.disable()
});

// Upload Image File - Only allow upload when file is selected
document.getElementById("file").onchange = function () {
    if (this.files[0].name !== true && this.files[0].name !== null) {
        document.getElementById("uploadFile").value = this.files[0].name;
        document.getElementById('submit-button').MaterialButton.enable()
    }
};

// Open the Logging dialog
var loggingDialog = document.getElementById('logging-dialog');
var showLoggingnav = document.getElementById('show-logging-nav');
showLoggingnav.addEventListener('click', function () {
    loggingDialog.showModal();
});

// Close the logging dialog
document.getElementById('close-logging-dialog').addEventListener('click', function () {
    loggingDialog.close();
    document.getElementById("uploadFile").value = null;
    //document.getElementById('logging-submit-button').MaterialButton.disable()
});

// Submit logging message
document.getElementById('logging-submit-button').addEventListener('click', function () {
    var levelDiv = document.getElementById('logging-level');
    var level = levelDiv.options[levelDiv.selectedIndex].value;
    var message = document.getElementById('log-message-field').value;
    gapi.client.computeTraining.logging.put({
        'level': level,
        'message': message
    }).execute(function (resp) {
        console.log(resp)
    })
});

//  Functions to run at start
function init() {

    // Callback URL for ROOT with gapi
    if (window.location.host.indexOf("localhost") > -1) {
        // For dev server running on localhost - needs special localhost link
        var ROOT = '//' + window.location.host + '/_ah/api'
    } else if (window.location.host.indexOf("127.0.0.1") > -1) {
        // For dev server running on 127.0.0.1, needs http, not https
        var ROOT = 'http://' + window.location.host + '/_ah/api'
    } else {
        // For production use https else will fail gapi call
        var ROOT = 'https://' + window.location.host + '/_ah/api'
    }

    // Load the Google API
    gapi.client.load(
        'computeTraining',
        'v1',
        function () {
            //  Boot any methods for after apis load
            window.postInitiation();
        },
        ROOT
    );
}


//  Load Google APIs to communicate with App Engine Endpoints
window.postInitiation = function () {
    console.log("Api pinged successfully.  Normally you don't show this but for "
    + "troubleshooting purposes during the class, here it is:")
    console.log(gapi);

    // Get blobstore upload URL for adding new images
    gapi.client.computeTraining.blobstore.getUrl().execute(function (resp) {
        //console.log("Blobstore upload url:")
        //console.log(resp)
        document.getElementById("upload-form").action = resp['url'];
    });

    render();

    drawcat();
};

// Render all of the image cards
render = function (waitTime=0) {

    // Get the spinner for control
    var spinner = document.getElementById("spinner-container");
    spinner.style.display = 'block';

    // Get a list of all the uploaded images
    gapi.client.computeTraining.images.list().execute(function (resp) {
        console.log("Images for card generation:")
        console.log(resp);

        // Hide the loading spinner
        document.getElementById("spinner-container").style.display = "none";

        if (resp.items) {
            generateCards(resp.items);
        }
    });
};

deleteCard = function (evt) {
    var id = evt.target.idParam;
    gapi.client.computeTraining.images.delete({
        'id': id
    }).execute(function () {
        var card = document.getElementById(id);
        card.style.display = 'none';
    })
};

// Generate cards for each of the images from datastore
generateCards = function (list) {
    i = 0;
    for (; list[i];) {
        //console.log(list[i]);

        // Parse out data
        var card = document.createElement('div');
        card.className = 'demo-card-square mdl-card mdl-shadow--2dp';
        card.id = list[i].id;

        var title = document.createElement('div');
        title.className = 'mdl-card__title mdl-card--expand';
        title.style = "background: url('.." + list[i].img_url + "') bottom right 15% no-repeat;position: relative;";

        var heading = document.createElement('h2');
        heading.className = 'mdl-card__title-text';

        var imgLink = document.createElement('a');
        imgLink.style = "position:absolute;left:0;display:inline-block;width:100%;height:100%;text-decoration:none;";
        imgLink.href = "/fullimg?blob_key=" + list[i].blob_key;
        imgLink.target = "_blank";

        var characteristics = document.createElement('div');
        characteristics.className = 'mdl-card__supporting-text';

        var titleText = document.createTextNode(list[i].filename);
        var characteristicsText = document.createTextNode((list[i].characteristics.join(", ")));

        var deleteIcon = document.createElement('i');
        deleteIcon.className = 'material-icons delete-icon';
        deleteIcon.id = 'delete-' + list[i].id;
        var deleteIconText = document.createTextNode('close');
        deleteIcon.appendChild(deleteIconText);

        var emoji = document.createElement('img');
        emoji.className = 'card-emoji';
        var cats = (String(list[i].characteristics).match(/cat/g) || []).length;
        if (cats > 4) {
            // It's a 5 cat!
            emoji.src = '/cat5.png';
        } else if (cats > 3) {
            // It's a 4 cat!
            emoji.src = '/cat4.png';
        } else if (cats > 2) {
            // It's a 4 cat!
            emoji.src = '/cat3.png';
        } else if (cats > 1) {
            // It's a 4 cat!
            emoji.src = '/cat2.png';
        } else if (cats > 0) {
            // It's a 4 cat!
            emoji.src = '/cat1.png';
        } else {
            // It's not a cat >:(
            emoji.src = '/prohibited.png';
        }

        // Put it all together
        heading.appendChild(titleText);
        title.appendChild(heading);
        title.appendChild(emoji);
        title.appendChild(imgLink);
        characteristics.appendChild(characteristicsText);
        card.appendChild(title);
        card.appendChild(characteristics);
        card.appendChild(deleteIcon);


        // Add to dom
        componentHandler.upgradeElement(card);
        document.getElementById('container').appendChild(card);

        // Add the delete event listeners
        var listId = list[i].id;
        var icon = document.querySelector('#delete-' + listId);

        icon.addEventListener('click', deleteCard, listId);
        icon.idParam = listId;

        // Cycle to next image
        i++;
    }
    ;


};

// Cookie functions for storing values across page loads
function setCookie(cname, cvalue, exdays) {
    var d = new Date();
    d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
    var expires = "expires=" + d.toUTCString();
    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}

function getCookie(cname) {
    var name = cname + "=";
    var ca = document.cookie.split(';');
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}

function drawcat() {
    // Meow
    console.log('                \n' +
        '              You found Tango!\n' +
        '                \n' +
        '          ,.                 .,\'\n' +
        '\'         ,: \':.    .,.    .:\' :,\'\n' +
        '\'         ,\',   \'.:\'   \':.\'   ,\',\'\n' +
        '\'         : \'.  \'         \'  .\' :\'\n' +
        '\'         \', : \'           \' : ,\'\'\n' +
        '\'         \'.\' .,:,.   .,:,. \'.\'\'\n' +
        '\'          ,:    V \'. .\' V    :,\'\n' +
        '\'         ,:        / \'        :,\'\n' +
        '\'         ,:                   :,\'\n' +
        '\'          ,:       =:=       :,\'\n' +
        '\'           ,: ,     :     , :,\'\n' +
        '\'            :\' \',.,\' \',.,:\' \':\'\n' +
        '\'           :\'      \':WW::\'   \'.\'\n' +
        '\'          .:\'       \'::::\'   \':\'\n' +
        '\'          ,:        \'::::\'    :,\'\n' +
        '\'          :\'         \':::\'    \':\'\n' +
        '\'         ,:           \':\'\'     :.\'\n' +
        '\'        .:\'             \'.     \',.\'\n' +
        '\'       ,:\'               \'\'     \'.\'\n' +
        '\'       .:\'               .\',    \':\'\n' +
        '\'      .:\'               .\'.,     :\'\n' +
        '\'      .:                .,\'\'     :\'\n' +
        '\'      ::                .,\'\'    ,:\'\n' +
        '\'      ::              .,\'\',\'   .:\'\'\n' +
        '\'    .,::\'.           .,\',\'     ::::.\'\n' +
        '\'  .:\'     \',.       ,:,       ,WWWWW,\'\n' +
        '\'  :\'        :       :W:\'     :WWWWWWW,          .,.\'\n' +
        '\'  :         \',      WWW      WWWWWWWWW          \'::,\'\n' +
        '\'  \'.         \',     WWW     :WWWWWWWWW            \'::,\'\n' +
        '\'   \'.         :     WWW     :WWWWWWWW\'             :::\'\n' +
        '\'    \'.       ,:     WWW     :WWWWWWW\'             .:::\'\n' +
        '\'     \'.     .W:     WWW     :WWWWWW\'           .,:::\'\'\n' +
        '\'      \'.   :WW:     WWW     :WWWWW\'      .,,:::::\'\'\'\n' +
        '\'     .,\'   \'\'::     :W:     :WWWWW.  .,::::\'\'\'\n' +
        '\'  ,\'        \'\'\',\'\',\',\',\'\',\'\'\'WWWWW::::\'\'\'\n' +
        '\'   \':,,,,,,,\':  :  : : :  :  :WWWW\'\'\'');
}