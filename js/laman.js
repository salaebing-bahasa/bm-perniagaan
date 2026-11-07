/* Menu mudah alih dan butang sembunyikan terjemahan · เมนูมือถือและปุ่มซ่อนคำแปล */
(function () {
  var togol = document.querySelector(".togol-nav");
  var nav = document.getElementById("nav-utama");
  if (togol && nav) {
    togol.addEventListener("click", function () {
      var buka = nav.classList.toggle("buka");
      togol.setAttribute("aria-expanded", buka ? "true" : "false");
    });
  }

  var th = document.getElementById("togol-th");
  if (th) {
    var simpan = function (v) { try { localStorage.setItem("bmp-tanpa-th", v ? "1" : "0"); } catch (e) {} };
    var set = function (v) {
      document.body.classList.toggle("tanpa-th", v);
      th.setAttribute("aria-pressed", v ? "true" : "false");
      th.textContent = v ? "Tunjuk terjemahan · แสดงคำแปล" : "Sembunyikan terjemahan · ซ่อนคำแปล";
    };
    var awal = false;
    try { awal = localStorage.getItem("bmp-tanpa-th") === "1"; } catch (e) {}
    set(awal);
    th.addEventListener("click", function () {
      var v = !document.body.classList.contains("tanpa-th");
      set(v); simpan(v);
    });
  }
})();
