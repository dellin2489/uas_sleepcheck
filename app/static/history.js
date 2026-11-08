// Konfirmasi sebelum menghapus data
document.querySelectorAll(".form-hapus").forEach(function (form) {
  form.addEventListener("submit", function (e) {
    var nama = form.dataset.nama || "ini";
    if (!confirm('Yakin ingin menghapus data "' + nama + '"?')) {
      e.preventDefault();
    }
  });
});

// Pencarian nama (nilai tambah)
var inputCari = document.getElementById("cari-nama");
if (inputCari) {
  var jumlah = document.getElementById("jumlah-data");
  var kosong = document.getElementById("tidak-ditemukan");
  var baris = document.querySelectorAll(".history-table tbody tr");

  inputCari.addEventListener("input", function () {
    var kata = inputCari.value.trim().toLowerCase();
    var tampil = 0;
    baris.forEach(function (row) {
      var nama = row.querySelector(".kolom-nama").textContent.toLowerCase();
      var cocok = nama.includes(kata);
      row.style.display = cocok ? "" : "none";
      if (cocok) tampil++;
    });
    if (jumlah) jumlah.textContent = tampil + " data";
    if (kosong) kosong.style.display = tampil === 0 ? "" : "none";
  });
}
