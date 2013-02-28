<h2>Cvičení</h2>

<table class="table table-hover">
    <thead>
        <tr>
            <th>Cvičení</th>
            %if showLector:
                <th>Cvičící</th>
            %end
            <th>Stav</th>
            <th>Akce</th>
        </tr>
     </thead>
    
    <tbody>
        %lecture = None
        %for lecture in lectures:
        <tr>
            <td>{{lecture.name}}</td>
            %if showLector:
                <td>{{lecture.lector}}</td>
            %end
            <td>
                <div class='btn-group'>
                    %if lecture.state:
                        <span class='btn btn-mini btn-success active' style='cursor:default' ><i class="icon-ok icon-white"></i></span>
                        <a href='?deactivate={{lecture.lecture_id}}' class='btn btn-mini'> <i class="icon-remove"></i></a>
                    %else:
                        <a href='?activate={{lecture.lecture_id}}' class='btn btn-mini'><i class="icon-ok"></i></a>
                        <span class='btn btn-mini btn-danger active' style='cursor:default'> <i class="icon-remove icon-white"></i></span>
                    %end
                </div>    
            </td>
            <td>     
                <a href='/lectures/run/{{lecture.lecture_id}}'><i class="icon-eye-open"></i> otestovat</a>
                <a href='/lectures/edit/{{lecture.lecture_id}}'><i class="icon-pencil"></i> upravit</a>
                <a href='/lectures/delete/{{lecture.lecture_id}}'><i class="icon-remove"></i> smazat</a>
            </td>
        </tr>
        %end
        
        %if not lecture:
            <td colspan='{{4 if showLector else 3}}'>Zatím zde nejsou žádné cvičení.</td>
        %end
        
    </tbody>
</table>

<form action="" method="post" class="input-append" >
      <input type='text' name='add' placeholder="Jméno">
      <button class="btn" type="submit"><i class="icon-plus"></i> Přidat cvičení</button>
</form>

%rebase layout