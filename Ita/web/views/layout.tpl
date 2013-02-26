<!DOCTYPE html>
<html lang="cs">
  <head>
    <meta charset="utf-8">
    <title>{{title+" - " if defined("title") else ""}}ASM</title>
    <link href="/static/bootstrap.min.css" rel="stylesheet">

    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- Le styles -->
    <style type="text/css">
      body {
        padding-top: 20px;
        padding-bottom: 40px;
      }

      /* Custom container */
      .container-narrow {
        margin: 0 auto;
        max-width: 700px;
      }
      .container-narrow > hr {
        margin: 30px 0;
      }

    </style>
  </head>

  <body>

    <div class="container-narrow">

    <div class="masthead">
    <ul class="nav nav-pills pull-right">
        %print("url",requestedURL)
        %for ero in getMenu():
        % link, desc = ero[:2]
        %print(link)
            <li class="{{"active" if requestedURL.startswith(link) else ""}}"><a href="{{link}}">{{desc}}</a></li>
        %end
    </ul>
    
    <h3 class="muted">GZZA</h3>


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
        <p>DIP Aleš Tomeček 2013</p>
        %if not user:
            <a href="/login?lector=1">
                přihlášení cvičící
            </a>
        %end
      </div>

    </div> <!-- /container -->


<html>
<head>
</head>
