// not used yet
Dropzone.autoDiscover = false;
const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

const profileDropzone = new Dropzone("#profile-picture-dropzone", {
    url: "/accounts/upload/profile-picture/",
    headers: { "X-CSRFToken": csrftoken },
    paramName: "profile_image",
    maxFiles: 1,
    maxFilesize: 5, // MB
    autoProcessQueue: false,
    acceptedFiles: "image/*",
    clickable: "#profile-picture-dropzone",
    addRemoveLinks: true,
    previewTemplate: `
	       <div class="dz-preview dz-file-preview mt-4">
	           <img data-dz-thumbnail class="h-32 w-32 rounded-full object-cover mx-auto" />
	           <div class="dz-details mt-2 text-center">
	               <div class="dz-filename">
	                   <span data-dz-name class="text-sm font-medium text-gray-800 dark:text-white/90"></span>
	               </div>
	               <div class="dz-size">
	                   <span data-dz-size class="text-xs text-gray-500 dark:text-gray-400"></span>
	               </div>
	           </div>
	           <div class="dz-progress mt-2 h-2 w-full bg-gray-200 rounded-full overflow-hidden">
	               <div class="dz-upload h-full bg-brand-500 dark:bg-warning-300" data-dz-uploadprogress style="width:0%;"></div>
	           </div>
	           <div class="dz-error-message mt-2 text-sm text-red-500" data-dz-errormessage></div>
	       </div>
	   `,
    createImageThumbnails: true,
    renameFile: function (file) {
        const ext = file.name.split('.').pop();
        const newName = "profile_" + Date.now() + "." + ext;
        return newName;
    },
});

// Hide placeholder on added file
profileDropzone.on("addedfile", function (file) {
    if (this.files.length > 1) this.removeFile(this.files[0]);
    const dzMessage = document.querySelector("#profile-picture-dropzone .dz-message");
    if (dzMessage) dzMessage.style.display = "none";
});

// Restore placeholder if file removed
profileDropzone.on("removedfile", function (file) {
    const dzMessage = document.querySelector("#profile-picture-dropzone .dz-message");
    if (dzMessage) dzMessage.style.display = "block";
});

// Progress bar updates automatically
profileDropzone.on("uploadprogress", function (file, progress) {
    const progressElement = file.previewElement.querySelector(".dz-upload");
    progressElement.style.width = progress + "%";  // Fill the bar
});

// Trigger upload on Save Changes
document.getElementById("saveChangesBtn").addEventListener("click", function (e) {
    e.preventDefault();
    if (profileDropzone.files.length > 0) {
        profileDropzone.processQueue();
    } else {
        console.log("No file to upload");
    }
});

// Upload success
profileDropzone.on("success", function (file, response) {
    const newImageUrl = response.avatar_url;

    document.querySelectorAll(".profile-picture").forEach(img => {
        img.src = newImageUrl + "?t=" + new Date().getTime();
    });
    console.log("Response url: ", response);
    showToast("Profile picture updated successfully!", "success", "Upload Complete");
});

// Upload error
profileDropzone.on("error", function (file, errorMessage) {
    showToast("There was an error uploading the profile picture.", "error", "Upload Failed");
});