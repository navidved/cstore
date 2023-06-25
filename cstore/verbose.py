class Verbose:
    # TODO: completed verbose for all app

    def action(self, state, verbose_kind, **data):
        if state['verbose']:
            match verbose_kind:
                case "tag":
                    self.tag_verbose(**data)

    def tag_verbose(self, **data):
        if data["is_new_tag"]:
            print(
                f"Tag '{data['tag_obj'].name}' created. (id={data['tag_obj'].id})")
        else:
            print(
                f"Tag '{data['tag_obj'].name}' loaded. (id={data['tag_obj'].id})")
