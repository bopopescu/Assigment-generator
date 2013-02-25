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
            <td></td>
        </tr>
        %end
    </tbody>
</table>

%rebase layout