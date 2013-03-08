<h2>Zadání</h2>

<ul>
    %lecture = None
    %for lecture in lectures:
        <li><a href="/assigments/{{lecture.lecture_id}}">{{lecture.name}} <i class="icon-arrow-right"></i></a></li>
    %end
    %if not lecture:
        <li>V současné chvíli nejsou přístupná žádná cvičení</li>
    %end
</ul>

%rebase layout