<h2>Cvičící</h2>

<table class="table table-hover">
    <thead>
        <tr>
            <th>Login</th>
            <th>Master</th>
            <th>Akce</th>
        </tr>
     </thead>
    
    <tbody>
        %lector = None
        %for lector in lectors:
        <tr>
            <td>{{lector.login}}</td>
            <td>
                <div class='btn-group'>
                    %if lector.inRole("master"):
                        <span class='btn btn-mini btn-success active' style='cursor:default' ><i class="icon-ok icon-white"></i></span>
                        <a href='?degrade={{lector.login}}' class='btn btn-mini'> <i class="icon-remove"></i></a>
                    %else:
                        <a href='?promote={{lector.login}}' class='btn btn-mini'><i class="icon-ok"></i></a>
                        <span class='btn btn-mini btn-danger active' style='cursor:default'> <i class="icon-remove icon-white"></i></span>
                    %end
                </div>    
            </td>

            <td><a href='/lectors/delete/{{lector.login}}'><i class="icon-remove"></i> smazat</a> </td>
        </tr>
        %end
    </tbody>
</table>

<form action="" method="post" class="input-append" >
      <input type='text' name='add' placeholder="Jméno">
      <button class="btn" type="submit"><i class="icon-plus"></i> Přidat cvičícího</button>
</form>

%rebase layout