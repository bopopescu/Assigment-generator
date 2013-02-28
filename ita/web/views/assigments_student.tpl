<h2>Zadání</h2>

<ul>
    %for lecture in lectures:
    <li><a href="/assigments/{{lecture.lecture_id}}">{{lecture.name}} <i class="icon-arrow-right"></i></a></li>
    %end
</ul>

%rebase layout