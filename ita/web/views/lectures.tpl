<h2>Cvičení</h2>

<table class="table table-hover">
    <thead>
        <tr>
            <th>Cvičení</th>
            %if showLector:
                <th>Cvičící</th>
            %end
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
            <td><a href='/lectures/edit/{{lecture.lecture_id}}'><i class="icon-pencil"></i> upravit</a>
                <a href='/lectures/delete/{{lecture.lecture_id}}'><i class="icon-remove"></i> smazat</a> </td>
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