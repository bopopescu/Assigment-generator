<h2>Skupiny</h2>

<table class="table table-hover">
    <thead>
        <tr>
            <th>Skupina</th>
            <th>Čas</th>
            %if showLector:
                <th>Cvičící</th>
            %end
            <th>Akce</th>
        </tr>
     </thead>
    
    <tbody>
        %for group in groups:
        <tr>
            <td>{{group.data["name"]}}</td>
            <td></td>
            %if showLector:
                <td>{{group.lector}}</td>
            %end
            <td><a href='/groups/edit/{{group.data["group_id"]}}'><i class="icon-pencil"></i> upravit</a>
                <a href='/groups/delete/{{group.data["group_id"]}}'><i class="icon-remove"></i> smazat</a> </td>
        </tr>
        %end
        
        %if not group:
            <td colspan='{{4 if showLector else 3}}'>Zatím zde nejsou žádné skupiny.</td>
        %end
        
    </tbody>
</table>

<form action="" method="post" class="input-append" >
      <input type='text' name='add' placeholder="Jméno">
      <button class="btn" type="submit"><i class="icon-plus"></i> Přidat skupinu</button>
</form>

%rebase layout