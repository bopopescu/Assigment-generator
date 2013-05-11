<div style='float:right;'>
<div><a href='/assigments'><i class="icon-chevron-left"></i> zpátky na seznam</a></div>
</div>

<h2>{{lecture.name}}</h2>

<pre>
{{assigment.text}}
</pre>


%if assigment.locked:
<pre>
%try:
{{assigment.response or ""}}
%except UnicodeDecodeError:
Binární soubor
%end
</pre>

<div> <i class="icon-lock"></i> Možnost odpovídat je zamčená</div>

%else:

<form action='' method='post' enctype="multipart/form-data">

    <h2>Nahrát řešení</h2>

        <div class="uploadUjo">
            <div style="display:table;">
                <div class="ebleco" >
                    <div><i class="icon-upload"></i> Vyberte soubor procházením</div>
                    <div><input type="file" name="response" id="fileUpload"></div>
                    <div><input type='submit' value="Nahrát" class="btn" /></div>
                </div>
                <div class="ebleco notFirst" id="dragKajDrop">
                    <div><i class="icon-hand-up"></i> Přetáhnětě soubor se řešením</div>
                    <div id="dropzone">
                    <div id="dragHint" >umístěte soubor zde</div>
                     </div>
                </div>
            </div>    
            
            <div id="dragProgress">
                <div class="progress progress-success progress-striped">
                    <div class="bar" style="width: 1%"></div>
                </div>
            </div>
            <div id="dragMessages">
            </div>
        </div>
    
                

    
</form>
%end


%def scripts():
<script src="/static/jquery.filedrop.js" type="text/javascript" language="JavaScript"></script>

<script type="text/javascript" language="JavaScript">
$(".alert").alert();

$("#dragKajDrop").css("display","table-cell");

$('#dropzone').filedrop({
    fallback_id: 'fileUpload',   // an identifier of a standard file input element
    url: '',              // upload handler, handles each file separately, can also be a function returning a url
    paramname: 'response',          // POST parameter name used on serverside to reference file
    withCredentials: true,          // make a cross-origin request with cookies
    error: function(err, file) {
        switch(err) {
            case 'BrowserNotSupported':
                $("#dragKajDrop").hide();
                break;
            case 'TooManyFiles':
                alert("Je povolen pouze 1 soubor");
                break;
            case 'FileTooLarge':
                alert("Soubor je příliš veliký.\n Maximální velikost je 1MB.");
                // program encountered a file whose size is greater than 'maxfilesize'
                // FileTooLarge also has access to the file which was too large
                // use file.name to reference the filename of the culprit file
                break;
            case 'FileTypeNotAllowed':
                //podporujeme všechny typy
            default:
                break;
        }
    },
    maxfiles: 1,
    maxfilesize: 1,    // max file size in MBs
    dragOver: function() {
        // user dragging files over #dropzone
    },
    dragLeave: function() {
        // user dragging files out of #dropzone
    },
    docOver: function() {
        // user dragging files anywhere inside the browser document window
        $("#dragHint").fadeIn(100);
    },
    docLeave: function() {
        // user dragging files out of the browser document window
        $("#dragHint").fadeOut(200);
    },
    drop: function() {
        $("#dragHint").hide();
    },

    uploadStarted: function(i, file, len){
        // a file began uploading
        // i = index => 0, 1, 2, 3, 4 etc
        // file is the actual file of the index
        // len = total files user dropped
        $("#dragProgress").show();
        $("#dragProgress .bar").css("width","0%");
        $("#dragProgress").fadeIn(50);
        
    },
    
    uploadFinished: function(i, file, response, time, xhr) {
        var currentdate = new Date();
        var timeMsg = "<strong>" + currentdate.getHours() + ":" + (currentdate.getMinutes()<10 ? "0" : "") + currentdate.getMinutes() + "</strong> ";
    
        if(xhr.status != 200){
            response = {msg : xhr.statusText, type : "error"};
        }
    
        var msg = $("<div>");
        msg.addClass("alert fade in");
        msg.addClass("alert-"+response.type);
        msg.html('<button type="button" class="close" data-dismiss="alert">&times;</button> ' + timeMsg + response.msg );
        $("#dragMessages").prepend(msg);
    },
    progressUpdated: function(i, file, progress) {
        // this function is used for large files and updates intermittently
        // progress is the integer value of file being uploaded percentage to completion
        $("#dragProgress .bar").css("width",progress+"%");
    },
    beforeEach: function(file) {
        // file is a file object
        // return false to cancel upload
    },
    beforeSend: function(file, i, done) {
        // file is a file object
        // i is the file index
        // call done() to start the upload
        done();
    },
    afterAll: function() {
        // runs after all files have been uploaded or otherwise dealt with
         $("#dragProgress").fadeOut(1000);
    }
});
</script>
%end

%rebase layout scripts = scripts