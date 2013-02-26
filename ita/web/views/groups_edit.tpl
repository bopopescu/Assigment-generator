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
            <th>Akce</th>
        </tr>
     </thead>
    
    <tbody>
        %member = None
        %for member in group.members:
        <tr>
            <td>{{member.login}}</td>
            <td><a href='?remove={{member.login}}'><i class="icon-remove"></i> smazat</a> </td>
        </tr>
        %end
        
        %if not member:
            <td colspan='2'>V této skupině nejsou zatím žádní studenti</td>
        %end
    </tbody>
    
    
    
</table>

<form action="" method="post" class="form-inline" >
      <input type='text' name='add' id='inputLogin' placeholder="Login">
      <input type='submit' value='Přidat studenta' class="btn">

</form>


%rebase layout