<h2>Zadání</h2>
<h2>Čekající na ohodnocení</h2>
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
            <td>{{assigment.changed or assigment.generated}}</td>
            <td>
                %if assigment.locked:
                    <i class="icon-lock"></i>
                %end            
                {{lecture.name}}
            </td>
            %if showLector:
                <td>{{lecture.lector}}</td>
            %end
            <td>{{assigment.login}}</td>
            <td>     
                <a href='/assigments-lector/download/{{assigment.assigment_id}}'><i class="icon-download"></i> stáhnout</a>
                <a href='/assigments-lector/{{assigment.assigment_id}}'><i class="icon-wrench"></i> spravovat</a>
            </td>
        </tr>
        %end
        
        %if not assigment:
            <td colspan='{{5 if showLector else 4}}'>Zatím zde nejsou žádné zadání.</td>
        %end
    </tbody>
</table>


<h2>Ostatní zadání</h2>
<table class="table table-hover muted">
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
        %for assigment in silent:
        %lecture = assigment.getLecture()
        <tr>
            <td>{{assigment.changed or assigment.generated}}</td>
            <td>
                %if assigment.locked:
                    <i class="icon-lock"></i>
                %end            
                {{lecture.name}}
            </td>
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
            <td colspan='{{5 if showLector else 4}}'>Zatím zde nejsou žádné zadání.</td>
        %end
    </tbody>
</table>

%rebase layout