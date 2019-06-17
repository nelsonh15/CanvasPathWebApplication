var coll = document.getElementsByClassName("collapsible_prof_info");
var i
var col2 = document.getElementsByClassName("collapsible_students_list");
var j

collapsible(coll, i);
collapsible(col2, j);

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