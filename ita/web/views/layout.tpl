<!DOCTYPE html>
<html lang="cs">
  <head>
    <meta charset="utf-8">
    <title>{{title+" - " if defined("title") else ""}}ASM</title>
    <link href="/static/bootstrap.min.css" rel="stylesheet">
    <link href="/static/mia.css" rel="stylesheet">

    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- Le styles -->

  </head>

  <body>

    <div class="container-narrow">

    <div class="masthead">
        <ul class="nav nav-pills pull-right">
            %for ero in getMenu():
            % link, desc, counter = ero[:3]
            % safe_name = slug(desc)
                <li class="{{"active" if requestedURL.startswith(link) else ""}}">
                    <a href="{{link}}">{{desc}}
                    %if counter != None:
                        <span id="badge_{{safe_name}}"" class="badge{{" badge-warning" if counter > 0 else ""}}">{{counter}}</span>
                    %end
                    </a>
                
                </li>
            %end
        </ul>
        
        <h3 class="muted"><a href='/'><abbr title="Generátor Zákeřných Asemblerových Zadání">GZAZ</abbr></a></h3>
    </div>
      
      <hr>
      
    %if defined("msgs"):
        %for msg in msgs:
            % txt,type = msg
            <div class='alert alert-{{type}}'>{{txt}}</div>
        %end
    %end

      

      %include

      <hr>

      <div class="footer">
        <div class="pull-right">DIP Aleš Tomeček 2013 (verze {{VERSION_CONTROL}})</div>
        
        %if not user:
            <div>
            <a href="/login?lector=1">
                přihlášení cvičící
            </a>
            </div>
        %end
      </div>

    </div> <!-- /container -->

<script src="/static/jquery-1.9.1.min.js" type="text/javascript" language="JavaScript"></script>

<script src="/static/bootstrap.min.js" type="text/javascript" language="JavaScript"></script>

%if user and user.inRole("lector"):
<script>

var checkCounter = function(){
    $.ajax( { url: "/assigments-lector/counter",
              cache: false,
            } ).done(function( data ) {
                        var status = data.status;
                        var count  = data.count;
                        var badge = $("#badge_Zadani");
                        var current = badge.html();
                        
                        if( status == "ok" ){
                            if(current != count){
                                badge.slideUp(400, function() {
                                                       if(count > 0) badge.addClass("badge-warning")
                                                       else badge.removeClass("badge-warning")
                                                       badge.html(data.count);
                                                    } );
                                badge.slideDown(400);
                            }
                        }else{
                            badge.removeClass("badge-warning").addClass("badge-important");
                        }

                        setTimeout(checkCounter, 5000);
                        }
                    );
    };

setTimeout(checkCounter, 5000);

</script>
%end

%if defined("scripts"): scripts()



<html>
<head>
</head>
