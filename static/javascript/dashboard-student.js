var coll = document.getElementsByClassName("collapsible_personal_info");
var i;
var coll1 = document.getElementsByClassName("collapsible_grades_info");
var j;
var coll2 = document.getElementsByClassName("collapsible_courses");
var k;
var coll3 = document.getElementsByClassName("collapsible_professor_info");
var l;
var coll4 = document.getElementsByClassName("collapsible_professor");
var m;

collapsible(coll, i);
collapsible(coll1, j);
collapsible(coll2, k);
collapsible(coll3, l);
collapsible(coll4, m);

function collapsible(coll, i) {
  for (i = 0; i < coll.length; i++) {
    coll[i].addEventListener("click", function () {
      this.classList.toggle("active");
      var content = this.nextElementSibling;
      if (content.style.display === "block") {
        content.style.display = "none";
      } else {
        content.style.display = "block";
      }
    });
  }
}


