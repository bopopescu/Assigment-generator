<div style='float:right;'>
<a href='/groups'><i class="icon-chevron-left"></i> zpátky na seznam</a>
</div>

<h2>Úprava skupiny {{group.data["name"]}}</h2>

{{!form}}

<h3>Studenti</h3>

<table class="table table-hover">
    <thead>
        <tr>
            <th>Login</th>
            <th>Bodů</th>
            <th>Akce</th>
        </tr>
     </thead>
    
    <tbody>
        %login = None
        %members = group.getResults()
        %for login in members:
        %points = members[login]
        <tr>
            <td>{{login}}</td>
            <td>{{points}}</td>
            <td><a href='?remove={{login}}'><i class="icon-remove"></i> smazat</a> </td>
        </tr>
        %end
        
        %if not login:
            <td colspan='3'>V této skupině nejsou zatím žádní studenti</td>
        %end
    </tbody>
    
    
    
</table>


<form action="" method="post" class="input-append" >
      <input type='text' name='add' placeholder="Login">
      <button class="btn" type="submit"><i class="icon-plus"></i> Přidat studenta</button>
</form>


%rebase layout