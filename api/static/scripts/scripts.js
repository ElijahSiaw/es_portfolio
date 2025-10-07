tailwind.config={
  'darkMode': 'class',
  theme: {
    extend: {
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-conic':
          'conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))',
		   'port-bg': `url("${location.origin}/static/images/bg.png")`,
      },
    },
  },
  plugins: [],
}

  function onToggleNav(){
      const menu = document.getElementById('toggle-menu')
      if (!menu.classList.contains('translate-x-full')) {
        document.body.style.overflow = 'auto';
      } else {
        document.body.style.overflow = 'hidden';
      }
      menu.classList.toggle('translate-x-full')
  };

async function toggleTheme(){
         const themeToggle = document.getElementById('theme-toggle');
    const toggleLight = document.getElementById('theme-toggle-light');
    const toggleDark = document.getElementById('theme-toggle-dark');
    const html = document.documentElement;

    // Check localStorage for theme
    if(localStorage.getItem('theme') === 'light') {
      html.classList.remove('dark');
      toggleLight.classList.add('hidden');
      toggleDark.classList.remove('hidden');
    } else {
      html.classList.add('dark');
      toggleLight.classList.remove('hidden');
      toggleDark.classList.add('hidden');
    }

      if(html.classList.contains('dark')) {
        html.classList.remove('dark');
        localStorage.setItem('theme', 'light');
        toggleLight.classList.add('hidden');
        toggleDark.classList.remove('hidden');
        const params = new URLSearchParams();
        params.set('theme','light');
        params.set('url',window.location.href)
        await fetch(`/api/theme?${params}`)
      } else {
        html.classList.add('dark');
        localStorage.setItem('theme', 'dark');
        toggleLight.classList.remove('hidden');
        toggleDark.classList.add('hidden');
        const params = new URLSearchParams();
        params.set('theme','dark');
        params.set('url',window.location.href)
        await fetch(`/api/theme?${params}`)
      }
    };
    async function handleShare(e){
    const title = e.dataset.shareTitle;
    const baseUrl = e.dataset.shareUrl;
  if (!('share' in navigator)) {
    return;
  }
    const shareData = {
      title: title,
      text: `Check out this post ${title} from Es Solution`,
      url: baseUrl,
    };
    if (navigator.canShare(shareData)) {
      try {
        await navigator.share(shareData);
      } catch (err) {
        if (err.name !== 'AbortError') {
          console.error(`${err.name}\n ${err.message}\n`);      
        }
      }
    }
}
 async function handleReaction(e){
   const reaction = e.dataset.userReaction;
   const userId = e.dataset.userId;
   const data = {
     reaction,
     userId
   }
   try{
   const response = await fetch(location.href, {method:'put',headers:{'content-type': 'application/json'}, body: JSON.stringify(data)})
   const res = await response.json()
   alert(res.message)
   }catch(err){
     console.log(err.message)
   }
 }
 
 async function handleSubmit(e){
   e.preventDefault();
   const form = document.getElementById("comment-form");
   const formData = new FormData(form);
   const data = Object.fromEntries(formData.entries());
   if(data.message.length >50){
     alert("Limit reached");
     return false;
   }
   try{
  const response = await fetch(form.action,{method: 'POST', headers:{'content-type':'application.json'}, body: JSON.stringify(data)});
  if(response.ok){
   const res = await response.json(); 
   alert(res.message)
  }
   }catch(err){
    alert(err.message)
   }
   return false
 }
    document.addEventListener('DOMContentLoaded', ()=>{
      const themeToggle = document.getElementById('theme-toggle');
    const toggleLight = document.getElementById('theme-toggle-light');
    const toggleDark = document.getElementById('theme-toggle-dark');
    const svg_wrapper = document.getElementById('svg-wrapper');
    const svg = document.querySelectorAll('svg');
    svg.forEach((el)=>{el.setAttribute('width', '200');
    el.setAttribute('height','160');});
    const html = document.documentElement;
      if(localStorage.getItem('theme') === 'light') {
      html.classList.remove('dark');
      toggleLight.classList.add('hidden');
      toggleDark.classList.remove('hidden');
    } else {
      html.classList.add('dark');
      toggleLight.classList.remove('hidden');
      toggleDark.classList.add('hidden');
    }
    setTimeout(()=>{svg_wrapper.style.opacity = '1'},200);
    })

  function removeFile(){
   const image = document.getElementById('image-wrapper');
	 const video = document.getElementById('video-wrapper');
	 const svg_wrapper = document.getElementById('svg-wrapper');
	 const remove = document.getElementById('remove-wrapper');
	 const wrapper = document.getElementById('file-wrapper');
	 const link = document.getElementById('link-wrapper');
	 svg_wrapper.classList.add('hidden');
	 video.classList.add('hidden')
	   video.src = "/";
	   image.classList.add('hidden')
	   image.src = "/"
	   wrapper.classList.remove('hidden')
	   link.classList.remove('hidden')
	   remove.classList.add('hidden')
  }
  function handleCopy(copy){
    if (navigator.clipboard) {
          navigator.clipboard.writeText(copy);
        }else{
      try {
        const body = document.querySelector("body");
    const textarea = document.createElement("textarea");
        body?.appendChild(textarea);
        textarea.value = copy;
        textarea.select();
        document.execCommand("copy");
        body?.removeChild(textarea);
        }catch (e) {
        alertService.error('Copy unsupported ' +e, {keepAfterRouteChange: false});
        }
        }
  }
	function handleChange(e){
	  const count = document.getElementById(`limit-${e.name}`);
	 let limit = 0;
	 if(e.name==='post'){
	   limit = 1000;
	 }else{
	   limit = 300;
	 }
	 count.textContent = `${e.value.length}/${limit}`;
	};
	
	const changeEvent = (e) =>{
    const file = e.files[0];
    if (file) {
      const pattern = /image-*/;
      if (!file.type.match(pattern)) {
        return videoEvent(file);
      }
}
	convertToBase64(file, 'image');
  };
const convertToBase64 = (file, type)=>{
	const reader = new FileReader();
	reader.readAsDataURL(file);
	reader.onload =()=>{
	  const mediaFile = reader.result;
	  const image = document.getElementById('image-wrapper')
	 const video = document.getElementById('video-wrapper')
	 const remove = document.getElementById('remove-wrapper')
	 const wrapper = document.getElementById('file-wrapper')
	 const link = document.getElementById('link-wrapper')
	  if(type==='image'){
	   image.classList.remove('hidden');
	   image.src = mediaFile;
	   video.classList.add('hidden');
	  }else{
	     video.classList.remove('hidden');
	   video.src = mediaFile;
	   image.classList.add('hidden');
	  }
		remove.classList.remove('hidden');
		link.classList.add('hidden');
		wrapper.classList.add('hidden');
	}
	reader.onerror =(e)=>{
		 alert(`Error: ${e}`)
	}
}
const videoEvent = (file) =>{
    if (file) {
      const pattern = /video-*/;

      if (!file.type.match(pattern)) {
        return alert('File type not supported');
      }
    }
	convertToBase64(file, 'video');
  };

function checkImageUrl(file){
  const image = document.createElement('img');
  image.src = file
  alert(file)
  alert(image.width)
  if(image.width > 0){
    return true
  }
  return false
}

const handleLink =(e)=>{
  const file = e.value;
  const video = document.createElement("video");
video.setAttribute("src", file);
video.addEventListener("canplay", function() {
  const link = document.getElementById('link-wrapper')
  const image = document.getElementById('image-wrapper');
	 const video = document.getElementById('video-wrapper');
	 const remove = document.getElementById('remove-wrapper');
	 const wrapper = document.getElementById('file-wrapper');
    if(video.videoHeight===0){
      const exists = checkImageUrl(file);
    if(exists) {
      image.classList.remove('hidden');
	   image.src = file;
	   video.classList.add('hidden');
	   wrapper.classList.add('hidden');
	   link.classList.add('hidden')
      return remove.classList.remove('hidden');
    }
    else {
      alert("Invalid link")
      return e.value = '';
    }
    };
    video.classList.remove('hidden');
	   video.src = file;
	   image.classList.add('hidden');
	   wrapper.classList.add('hidden');
	   link.classList.add('hidden')
		return remove.classList.remove('hidden');
});
video.addEventListener("error", function() {
  const image = document.getElementById('image-wrapper')
	 const video = document.getElementById('video-wrapper')
	 const remove = document.getElementById('remove-wrapper')
	 const wrapper = document.getElementById('file-wrapper')
  const exists = checkImageUrl(file)
    if(exists) {
      image.classList.remove('hidden')
	   image.src = file;
	   video.classList.add('hidden')
	   wrapper.classList.add('hidden')
	   link.classList.add('hidden')
      return remove.classList.remove('hidden');
    }
    else {
alert("Invalid link")
      return e.value = '';
    }
});
}

const changeProfileImage = (e) =>{
    const file = e.files[0];
    if (file) {
      const pattern = /image-*/;
      if (!file.type.match(pattern)) {
        return;
      }
}
const url = URL.createObjectURL(file);
const userImage = document.getElementById(`${e.name}-container`);
	 if(e.dataset.userPhoto){
	 const userInitials = document.getElementById('user-init');
	 const photoWrapper = document.getElementById('photo-wrapper');
	 const savePhotoButton = document.getElementById('save-photo-button');
	 savePhotoButton.classList.remove('hidden');
	 if(userInitials){
	 userInitials.classList.add('hidden');
	 }
	 photoWrapper.classList.add('hidden');
	 userImage.classList.remove('hidden')
	 userImage.setAttribute('src',url);
	 return
	 }
	 const coverPhotoWrapper = document.getElementById('cover-photo-wrapper');
	 const saveCoverPhotoButton = document.getElementById('save-cover-photo-button');
	 saveCoverPhotoButton.classList.remove('hidden');
	 coverPhotoWrapper.classList.add('hidden');
	 userImage.style.backgroundImage = `url('${url}')`;
  };
  
  function openDialog(){
   const modal = document.getElementById('bio-modal-dialog');
   document.body.style.overflow='hidden'
   modal.showModal();
  }
function openVideoDialog(e){
   const video_modal = document.getElementById('video-modal-dialog');
   const video_source = e.dataset.userVideo;
  const video = video_modal.querySelector('video');
  video.src = video_source;
   document.body.style.overflow='hidden'
   video_modal.showModal();
  }
function handleCloseDialog(){
  document.body.style.overflow = 'auto'
}
function closeDialog(e){
  const modal = document.getElementById('bio-modal-dialog');
   e.parentElement.close();
}
