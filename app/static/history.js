// Konfirmasi sebelum menghapus data
document.querySelectorAll(".form-hapus").forEach(function (form) {
  form.addEventListener("submit", function (e) {
    var tanggal = form.dataset.tanggal || "ini";
    if (!confirm('Yakin ingin menghapus riwayat tanggal "' + tanggal + '"?')) {
      e.preventDefault();
    }
  });
});

// Pencarian tanggal
var inputCari = document.getElementById("cari-tanggal");
if (inputCari) {
  var jumlah = document.getElementById("jumlah-data");
  var kosong = document.getElementById("tidak-ditemukan");
  var baris = document.querySelectorAll(".history-table tbody tr");

  inputCari.addEventListener("input", function () {
    var kata = inputCari.value.trim().toLowerCase();
    var tampil = 0;
    baris.forEach(function (row) {
      var tanggal = row.querySelector(".kolom-tanggal").textContent.toLowerCase();
      var cocok = tanggal.includes(kata);
      row.style.display = cocok ? "" : "none";
      if (cocok) tampil++;
    });
    if (jumlah) jumlah.textContent = tampil + " data";
    if (kosong) kosong.style.display = tampil === 0 ? "" : "none";
  });
}