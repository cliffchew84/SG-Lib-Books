/*
|-------------------------------------------------------------------------------
| Development config                      https://maizzle.com/docs/environments
|-------------------------------------------------------------------------------
|
| This is the base configuration that Maizzle will use when you run commands
| like `npm run build` or `npm run dev`. Additional config files will
| inherit these settings, and can override them when necessary.
|
*/
const data = await fetch('https://jsonplaceholder.typicode.com/todos').then(res => res.json())


/** @type {import('@maizzle/framework').Config} */
export default {
  build: {
    content: ['emails/**/*.html'],
    static: {
      source: ['images/**/*.*'],
      destination: 'images',
    },
  },
  books: [
    {
      BID: 205549460,
      TitleName: 'Steve Jobs / Walter Isaacson.',
      Author: 'Isaacson, Walter',
      cover_url: 'https://eservice.nlb.gov.sg/bookcoverwrapper/cover/9781982176860',
      url: 'https://sg-lib-books.web.app/dashboard/books/205549460',
      BranchName: ['Bedok Public Library', 'Clementi Public Library'],
    },
    {
      BID: 300077724,
      TitleName: 'Nexus : a brief history of ...',
      Author: 'Harari, Yuval N',
      cover_url: 'https://eservice.nlb.gov.sg/bookcoverwrapper/cover/9781911717096',
      url: 'https://sg-lib-books.web.app/dashboard/books/300077724',
      BranchName: ['Bedok Public Library', 'Clementi Public Library'],
    },
  ],
  email: "wongzhaowu@gmail.com"
}

