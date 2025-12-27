function businessImageUploader(uploadUrl) {
    return {
        uploadUrl,
        preview: null,
        file: null,
        uploading: false,

        handleFile(event) {
            const file = event.target.files[0];
            if (!file) return;

            // Validate type
            if (!['image/jpeg', 'image/jpg'].includes(file.type)) {
                showToast(
                    'Only JPG images are allowed',
                    'warning',
                    'Invalid file'
                );
                return;
            }

            // Validate size (5MB)
            if (file.size > 5 * 1024 * 1024) {
                showToast(
                    'Image must be less than 5MB',
                    'warning',
                    'File too large'
                );
                return;
            }

            this.file = file;

            // Preview
            this.preview = URL.createObjectURL(file);
        },

        async upload() {
            if (!this.file) {
                showToast('Please select an image first', 'warning');
                return;
            }

            this.uploading = true;

            try {
                const resp = await uploadBusinessImage(this.file, this.uploadUrl);

                if (!resp.ok) {
                    showToast('Upload failed', 'error', "Logo Upload Failed");
                    
                } 

                showToast('Your Business Logo was uploaded successfully', 'success', "Upload Complete");
            } catch (e) {
                showToast('Something went wrong, try again in a few minutes', 'error', "Upload Errors");
            } finally {
                this.uploading = false;
            }
        }
    };
};


async function uploadBusinessImage(file, endpoint) {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    const formData = new FormData();
    formData.append('logo_image', file);

    const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken
        },
        body: formData
    });

    return response;
};
