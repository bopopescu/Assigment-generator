<h2>Zadání</h2>

<table class="table table-hover">
    <thead>
        <tr>
            <th>Čas</th>
            <th>Cvičení</th>
            %if showLector:
                <th>Cvičící</th>
            %end

            <th>Student</th>

            <th>Akce</th>
        </tr>
     </thead>
    
    <tbody>
        %assigment = None
        %for assigment in assigments:
        %lecture = assigment.getLecture()
        <tr>
            <td></td>
            <td>{{lecture.name}}</td>
            %if showLector:
                <td>{{lecture.lector}}</td>
            %end
            <td>{{assigment.login}}</td>
            <td>     
                <a href='/assigments-lector/{{assigment.assigment_id}}'><i class="icon-wrench"></i> spravovat</a>
            </td>
        </tr>
        %end
        
        %if not assigment:
            <td colspan='{{4 if showLector else 3}}'>Zatím zde nejsou žádné zadání.</td>
        %end
    </tbody>
</table>

%rebase layout