export interface GitHubActivity {
    id: string;
    type: string;
    icon: string;
    title: string;
    description: string;
    time_ago: string;
    context: any;
}

export interface Post {
    id: number;
    post_content: string;
    post_type: string;
    status: string;
    created_at: number;
    published_at: number | null;
}

export interface Template {
    id: string;
    name: string;
    description: string;
    icon: string;
    context: any;
}

export interface PostContext {
    type: string;
    commits: number;
    repo: string;
    full_repo: string;
    date: string;
}
