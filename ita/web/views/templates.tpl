<h3>Šablony</h3>
%def getDir(path): return "/".join( path.split("/")[:-1] )

%paths = list(files.keys())
%paths.sort()

%stack = ["", ""]

<table class="table ">
    <thead>
        <tr>
            <th>Šablona</th>
            <th>Nonterminály</th>
        </tr>
     </thead>
     <tbody>
     
%for path in paths:
%file = path
%dirName = getDir(path)

%if dirName != stack[-1]:
    %stack.pop()
    <tr>
        <th colspan='2'>{{dirName[len(stack[-1]):]}}</th>
    </tr>
    %stack.append(dirName)
%end
    <tr>
        <td><a href='/templates/{{file}}'>{{file[len(stack[-1]):]}}</a></td>
        <td>{{", ".join(files[file].keys())}}</td>
    </tr>
%end    

</table>


%rebase layout