<div style='float:right;'>
<a href='/groups/add' class='btn'><i class="icon-plus"></i> přidat skupinu</a>
</div>

<h2>Skupiny</h2>

<table class="table table-hover">
    <thead>
        <tr>
            <th>Skupina</th>
            <th>Čas</th>
            <th>Akce</th>
        </tr>
     </thead>
    
    <tbody>
        %for group in groups:
        <tr>
            <td>{{group.data["name"]}}</td>
            <td></td>
            <td><a href='/groups/edit/{{group.data["group_id"]}}'><i class="icon-pencil"></i> upravit</a>
                <a href='/groups/delete/{{group.data["group_id"]}}'><i class="icon-remove"></i> smazat</a> </td>
        </tr>
        %end
    </tbody>
</table>

%rebase layout